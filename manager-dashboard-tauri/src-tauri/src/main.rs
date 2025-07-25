// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use serde::{Deserialize, Serialize};
use std::sync::{Arc, Mutex};
use reqwest;
use tauri::Manager;

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

#[tauri::command]
async fn http_get(url: String, headers: Option<String>) -> Result<String, String> {
    let client = reqwest::Client::new();
    let mut request = client.get(&url);
    
    // Add custom headers if provided
    if let Some(headers_str) = headers {
        if let Ok(headers_map) = serde_json::from_str::<std::collections::HashMap<String, String>>(&headers_str) {
            for (key, value) in headers_map {
                request = request.header(key, value);
            }
        }
    }
    
    let response = request
        .header("Accept", "application/json")
        .header("Content-Type", "application/json")
        .send()
        .await
        .map_err(|e| e.to_string())?;
    
    let status = response.status();
    let text = response.text().await.map_err(|e| e.to_string())?;
    
    if status.is_success() || status.as_u16() == 201 {
        Ok(text)
    } else {
        Err(format!("HTTP {}: {}", status, status.as_str()))
    }
}

#[tauri::command]
async fn http_post(url: String, body: String, headers: Option<String>) -> Result<String, String> {
    let client = reqwest::Client::new();
    let mut request = client.post(&url);
    
    // Add custom headers if provided
    if let Some(headers_str) = headers {
        if let Ok(headers_map) = serde_json::from_str::<std::collections::HashMap<String, String>>(&headers_str) {
            for (key, value) in headers_map {
                request = request.header(key, value);
            }
        }
    }
    
    let response = request
        .header("Accept", "application/json")
        .header("Content-Type", "application/json")
        .body(body)
        .send()
        .await
        .map_err(|e| e.to_string())?;
    
    let status = response.status();
    let text = response.text().await.map_err(|e| e.to_string())?;
    
    if status.is_success() || status.as_u16() == 201 {
        Ok(text)
    } else {
        Err(format!("HTTP {}: {}", status, status.as_str()))
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
            http_post
        ])
        .setup(|app| {
            let window = app.get_window("main").unwrap();
            
            // Enable devtools in development
            #[cfg(debug_assertions)]
            window.open_devtools();
            
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}