// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use serde::{Deserialize, Serialize};
use std::sync::{Arc, Mutex};
use reqwest;
use std::sync::atomic::{AtomicBool, Ordering};
use std::thread;
use std::time::{Duration, SystemTime, UNIX_EPOCH};

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

#[derive(Debug, Serialize, Deserialize, Clone)]
struct AppState {
    is_authenticated: bool,
    user_name: Option<String>,
    organization: Option<String>,
}

impl Default for AppState {
    fn default() -> Self {
        Self {
            is_authenticated: false,
            user_name: None,
            organization: None,
        }
    }
}

// Tauri commands
#[tauri::command]
fn authenticate_manager(
    state: tauri::State<'_, Arc<Mutex<AppState>>>,
    user_name: String,
    organization: String,
) -> Result<String, String> {
    let mut app_state = state.lock().map_err(|e| e.to_string())?;
    app_state.is_authenticated = true;
    app_state.user_name = Some(user_name);
    app_state.organization = Some(organization);
    
    Ok("Authentication successful".to_string())
}

#[tauri::command]
fn logout_manager(state: tauri::State<'_, Arc<Mutex<AppState>>>) -> Result<String, String> {
    let mut app_state = state.lock().map_err(|e| e.to_string())?;
    app_state.is_authenticated = false;
    app_state.user_name = None;
    app_state.organization = None;
    
    Ok("Logged out successfully".to_string())
}

#[tauri::command]
fn get_app_state(state: tauri::State<'_, Arc<Mutex<AppState>>>) -> Result<AppState, String> {
    let app_state = state.lock().map_err(|e| e.to_string())?;
    Ok(app_state.clone())
}

#[tauri::command]
fn fetch_team_data() -> Result<String, String> {
    // Simulate fetching team data from a server
    std::thread::sleep(std::time::Duration::from_millis(500));
    Ok("Team data fetched successfully".to_string())
}

#[tauri::command]
fn check_for_updates() -> Result<String, String> {
    // Simulate checking for updates
    std::thread::sleep(std::time::Duration::from_millis(300));
    Ok("No updates available".to_string())
}

// Global tracking state
static mut TRACKING_STATE: Option<Arc<Mutex<TrackingState>>> = None;
static mut SHOULD_STOP: Option<Arc<AtomicBool>> = None;

fn get_tracking_state() -> Arc<Mutex<TrackingState>> {
    unsafe {
        if TRACKING_STATE.is_none() {
            TRACKING_STATE = Some(Arc::new(Mutex::new(TrackingState {
                is_tracking: false,
                user_id: None,
                team_id: None,
                token: None,
            })));
        }
        TRACKING_STATE.as_ref().unwrap().clone()
    }
}

fn get_should_stop() -> Arc<AtomicBool> {
    unsafe {
        if SHOULD_STOP.is_none() {
            SHOULD_STOP = Some(Arc::new(AtomicBool::new(false)));
        }
        SHOULD_STOP.as_ref().unwrap().clone()
    }
}

#[tauri::command]
async fn start_tracking(
    user_id: String,
    team_id: String,
    token: String,
) -> Result<String, String> {
    let tracking = get_tracking_state();
    let mut tracking_guard = tracking.lock().map_err(|e| e.to_string())?;
    
    if tracking_guard.is_tracking {
        return Err("Tracking is already active".to_string());
    }
    
    tracking_guard.is_tracking = true;
    tracking_guard.user_id = Some(user_id);
    tracking_guard.team_id = Some(team_id);
    tracking_guard.token = Some(token);
    
    // Reset stop flag
    get_should_stop().store(false, Ordering::Relaxed);
    
    Ok("Tracking started successfully".to_string())
}

#[tauri::command]
async fn stop_tracking() -> Result<String, String> {
    let tracking = get_tracking_state();
    let mut tracking_guard = tracking.lock().map_err(|e| e.to_string())?;
    
    if !tracking_guard.is_tracking {
        return Err("Tracking is not active".to_string());
    }
    
    tracking_guard.is_tracking = false;
    tracking_guard.user_id = None;
    tracking_guard.team_id = None;
    tracking_guard.token = None;
    
    // Set stop flag
    get_should_stop().store(true, Ordering::Relaxed);
    
    Ok("Tracking stopped successfully".to_string())
}

#[tauri::command]
async fn get_current_activity() -> Result<String, String> {
    // Simulate getting current activity
    Ok("Currently active in Employee Tracker".to_string())
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

fn main() {
    let state = Arc::new(Mutex::new(AppState::default()));
    
    tauri::Builder::default()
        .manage(state)
        .invoke_handler(tauri::generate_handler![
            authenticate_manager,
            logout_manager,
            get_app_state,
            fetch_team_data,
            check_for_updates,
            http_get,
            http_post,
            start_tracking,
            stop_tracking,
            get_current_activity
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}