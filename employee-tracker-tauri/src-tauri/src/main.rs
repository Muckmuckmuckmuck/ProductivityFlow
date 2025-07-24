// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::{CustomMenuItem, SystemTray, SystemTrayMenu, SystemTrayMenuItem, SystemTrayEvent, Manager};
use serde::{Deserialize, Serialize};
use std::sync::{Arc, Mutex};
use std::time::{Duration, SystemTime, UNIX_EPOCH};
use std::thread;
use std::sync::atomic::{AtomicBool, Ordering};
use reqwest;


mod system_monitor;
use system_monitor::{get_active_window_info, get_idle_time};

#[derive(Debug, Serialize, Deserialize, Clone)]
struct ActivityData {
    active_app: String,
    window_title: String,
    idle_time: f64,
    timestamp: u64,
}

#[derive(Debug, Serialize, Deserialize)]
struct TrackingState {
    is_tracking: bool,
    user_id: Option<String>,
    team_id: Option<String>,
    token: Option<String>,
}

struct AppState {
    tracking: Arc<Mutex<TrackingState>>,
    should_stop: Arc<AtomicBool>,
}

impl Default for AppState {
    fn default() -> Self {
        Self {
            tracking: Arc::new(Mutex::new(TrackingState {
                is_tracking: false,
                user_id: None,
                team_id: None,
                token: None,
            })),
            should_stop: Arc::new(AtomicBool::new(false)),
        }
    }
}

#[tauri::command]
async fn start_tracking(
    state: tauri::State<'_, AppState>,
    user_id: String,
    team_id: String,
    token: String,
) -> Result<String, String> {
    let mut tracking = state.tracking.lock().map_err(|e| e.to_string())?;
    
    if tracking.is_tracking {
        return Err("Tracking is already active".to_string());
    }
    
    tracking.is_tracking = true;
    tracking.user_id = Some(user_id);
    tracking.team_id = Some(team_id);
    tracking.token = Some(token);
    
    // Start background monitoring thread
    let tracking_clone = state.tracking.clone();
    let should_stop = state.should_stop.clone();
    
    thread::spawn(move || {
        monitoring_loop(tracking_clone, should_stop);
    });
    
    Ok("Tracking started successfully".to_string())
}

#[tauri::command]
async fn stop_tracking(state: tauri::State<'_, AppState>) -> Result<String, String> {
    let mut tracking = state.tracking.lock().map_err(|e| e.to_string())?;
    
    if !tracking.is_tracking {
        return Err("Tracking is not active".to_string());
    }
    
    tracking.is_tracking = false;
    tracking.user_id = None;
    tracking.team_id = None;
    tracking.token = None;
    
    state.should_stop.store(true, Ordering::Relaxed);
    
    Ok("Tracking stopped successfully".to_string())
}



#[tauri::command]
async fn get_current_activity() -> Result<ActivityData, String> {
    let window_info = get_active_window_info().map_err(|e| e.to_string())?;
    let idle_time = get_idle_time().map_err(|e| e.to_string())?;
    
    let timestamp = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map_err(|e| e.to_string())?
        .as_secs();
    
    Ok(ActivityData {
        active_app: window_info.app_name,
        window_title: window_info.window_title,
        idle_time: idle_time.as_secs_f64(),
        timestamp,
    })
}

#[tauri::command]
async fn http_get(url: String) -> Result<String, String> {
    let client = reqwest::Client::new();
    
    let response = client
        .get(&url)
        .header("Accept", "application/json")
        .header("Content-Type", "application/json")
        .send()
        .await
        .map_err(|e| e.to_string())?;
    
    if response.status().is_success() {
        let text = response.text().await.map_err(|e| e.to_string())?;
        Ok(text)
    } else {
        Err(format!("HTTP {}: {}", response.status(), response.status().as_str()))
    }
}

#[tauri::command]
async fn http_post(url: String, body: String) -> Result<String, String> {
    let client = reqwest::Client::new();
    
    let response = client
        .post(&url)
        .header("Accept", "application/json")
        .header("Content-Type", "application/json")
        .body(body)
        .send()
        .await
        .map_err(|e| e.to_string())?;
    
    if response.status().is_success() {
        let text = response.text().await.map_err(|e| e.to_string())?;
        Ok(text)
    } else {
        Err(format!("HTTP {}: {}", response.status(), response.status().as_str()))
    }
}

#[tauri::command]
async fn send_activity_data(
    state: tauri::State<'_, AppState>,
    activity: ActivityData,
) -> Result<String, String> {
    let tracking = state.tracking.lock().map_err(|e| e.to_string())?;
    
    if !tracking.is_tracking {
        return Err("Tracking is not active".to_string());
    }
    
    // Here you would send the activity data to your backend
    // For now, we'll just log it
    println!("Activity data: {:?}", activity);
    
    Ok("Activity data sent successfully".to_string())
}

fn monitoring_loop(tracking: Arc<Mutex<TrackingState>>, should_stop: Arc<AtomicBool>) {
    while !should_stop.load(Ordering::Relaxed) {
        // Get activity data synchronously
        let window_info = get_active_window_info();
        let idle_time = get_idle_time();
        
        if let (Ok(window_info), Ok(idle_time)) = (window_info, idle_time) {
            let timestamp = SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap_or_default()
                .as_secs();
            
            let activity = ActivityData {
                active_app: window_info.app_name,
                window_title: window_info.window_title,
                idle_time: idle_time.as_secs_f64(),
                timestamp,
            };
            
            println!("Current activity: {:?}", activity);
        }
        
        thread::sleep(Duration::from_secs(30)); // Check every 30 seconds
    }
}

fn main() {
    let state = AppState::default();
    
    let quit = CustomMenuItem::new("quit".to_string(), "Quit");
    let show = CustomMenuItem::new("show".to_string(), "Show Window");
    let tray_menu = SystemTrayMenu::new()
        .add_item(show)
        .add_native_item(SystemTrayMenuItem::Separator)
        .add_item(quit);

    let system_tray = SystemTray::new().with_menu(tray_menu);

    tauri::Builder::default()
        .manage(state)
        .system_tray(system_tray)
        .invoke_handler(tauri::generate_handler![
            start_tracking,
            stop_tracking,
            get_current_activity,
            send_activity_data,
            http_get,
            http_post
        ])
        .on_system_tray_event(|app, event| match event {
            SystemTrayEvent::MenuItemClick { id, .. } => {
                match id.as_str() {
                    "quit" => {
                        std::process::exit(0);
                    }
                    "show" => {
                        let window = app.get_window("main").unwrap();
                        window.show().unwrap();
                        window.set_focus().unwrap();
                    }
                    _ => {}
                }
            }
            _ => {}
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
