// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::collections::{HashMap, HashSet};
use serde::{Deserialize, Serialize};
use tauri::{Manager, State, Window};
use tokio::sync::Mutex;

mod ollama;
mod config;
mod openwebui;

use ollama::*;
use config::*;

// Application state
#[derive(Default)]
struct AppState {
    models: Mutex<Vec<ModelData>>,
    starred_models: Mutex<HashSet<String>>,
    deletion_queue: Mutex<HashSet<String>>,
    config: Mutex<AppConfig>,
}

// Model data structure
#[derive(Debug, Clone, Serialize, Deserialize)]
struct ModelData {
    name: String,
    id: String,
    size: String,
    modified: String,
    age_category: String,
    capabilities: Vec<String>,
    status: String,
    is_liberated: bool,
    is_starred: bool,
    is_queued_for_deletion: bool,
    is_duplicate: bool,
    is_special_variant: bool,
    usage_info: Option<UsageInfo>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct UsageInfo {
    usage_count: u32,
    last_used: Option<String>,
    first_used: Option<String>,
    total_tokens: u64,
}

#[derive(Debug, Serialize, Deserialize)]
struct DeletionResult {
    deleted: Vec<String>,
    failed: Vec<String>,
}

// Load models from Ollama
#[tauri::command]
async fn load_models(
    state: State<'_, AppState>,
    window: Window,
) -> Result<Vec<ModelData>, String> {
    let _ = window.emit("status_update", "🔄 Loading models...");
    
    match get_ollama_models().await {
        Ok(models) => {
            let starred_models = state.starred_models.lock().await;
            let deletion_queue = state.deletion_queue.lock().await;
            
            let mut processed_models = Vec::new();
            
            for mut model in models {
                model.is_starred = starred_models.contains(&model.name);
                model.is_queued_for_deletion = deletion_queue.contains(&model.name);
                processed_models.push(model);
            }
            
            *state.models.lock().await = processed_models.clone();
            
            let _ = window.emit("status_update", format!("✅ Loaded {} models", processed_models.len()));
            Ok(processed_models)
        }
        Err(e) => {
            let _ = window.emit("status_update", "❌ Failed to load models");
            Err(format!("Failed to load models: {}", e))
        }
    }
}

// Toggle star status for a model
#[tauri::command]
async fn toggle_star(
    model_name: String,
    starred: bool,
    state: State<'_, AppState>,
) -> Result<(), String> {
    let mut starred_models = state.starred_models.lock().await;
    
    if starred {
        starred_models.insert(model_name);
    } else {
        starred_models.remove(&model_name);
    }
    
    // Save configuration
    let config = state.config.lock().await;
    if let Err(e) = save_app_config(&config, &starred_models).await {
        return Err(format!("Failed to save configuration: {}", e));
    }
    
    Ok(())
}

// Get detailed information about a model
#[tauri::command]
async fn get_model_details(model_name: String) -> Result<String, String> {
    match get_ollama_model_details(&model_name).await {
        Ok(details) => Ok(details),
        Err(e) => Err(format!("Failed to get model details: {}", e)),
    }
}

// Delete models from Ollama
#[tauri::command]
async fn delete_models(
    model_names: Vec<String>,
    state: State<'_, AppState>,
    window: Window,
) -> Result<DeletionResult, String> {
    let mut deleted = Vec::new();
    let mut failed = Vec::new();
    
    for model_name in model_names {
        let _ = window.emit("status_update", format!("🗑️ Deleting {}", model_name));
        
        match delete_ollama_model(&model_name).await {
            Ok(_) => {
                deleted.push(model_name.clone());
                
                // Remove from deletion queue and starred models
                let mut deletion_queue = state.deletion_queue.lock().await;
                let mut starred_models = state.starred_models.lock().await;
                deletion_queue.remove(&model_name);
                starred_models.remove(&model_name);
            }
            Err(e) => {
                println!("Failed to delete {}: {}", model_name, e);
                failed.push(model_name);
            }
        }
    }
    
    Ok(DeletionResult { deleted, failed })
}

// Load application configuration
#[tauri::command]
async fn load_config(state: State<'_, AppState>) -> Result<HashMap<String, Vec<String>>, String> {
    let starred_models = state.starred_models.lock().await;
    let mut config = HashMap::new();
    config.insert("starred_models".to_string(), starred_models.iter().cloned().collect());
    Ok(config)
}

// Save application configuration
#[tauri::command]
async fn save_config(
    config: HashMap<String, Vec<String>>,
    state: State<'_, AppState>,
) -> Result<(), String> {
    if let Some(starred_list) = config.get("starred_models") {
        let mut starred_models = state.starred_models.lock().await;
        *starred_models = starred_list.iter().cloned().collect();
        
        let app_config = state.config.lock().await;
        if let Err(e) = save_app_config(&app_config, &starred_models).await {
            return Err(format!("Failed to save configuration: {}", e));
        }
    }
    
    Ok(())
}

// Initialize the application
async fn initialize_app(app: &tauri::App) -> Result<(), Box<dyn std::error::Error>> {
    // Load configuration
    let config = load_app_config().await?;
    let starred_models = config.starred_models.clone();
    
    // Set up application state
    let state = AppState {
        models: Mutex::new(Vec::new()),
        starred_models: Mutex::new(starred_models),
        deletion_queue: Mutex::new(HashSet::new()),
        config: Mutex::new(config),
    };
    
    app.manage(state);
    
    Ok(())
}

fn main() {
    tauri::Builder::default()
        .setup(|app| {
            // Initialize the application synchronously
            tokio::runtime::Runtime::new().unwrap().block_on(async {
                if let Err(e) = initialize_app(app).await {
                    eprintln!("Failed to initialize app: {}", e);
                }
            });
            
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            load_models,
            toggle_star,
            get_model_details,
            delete_models,
            load_config,
            save_config
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
} 