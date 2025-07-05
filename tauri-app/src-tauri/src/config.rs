use std::collections::HashSet;
use std::path::PathBuf;
use serde::{Deserialize, Serialize};
use tokio::fs;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct AppConfig {
    pub starred_models: HashSet<String>,
    pub privacy_mode: bool,
    pub encrypt_database: bool,
    pub openwebui_integration: bool,
    pub last_updated: Option<String>,
}

// Get the configuration file path
fn get_config_path() -> Result<PathBuf, Box<dyn std::error::Error>> {
    let home_dir = dirs::home_dir()
        .ok_or("Could not find home directory")?;
    
    Ok(home_dir.join(".ollama_model_viewer_config.json"))
}

// Load application configuration
pub async fn load_app_config() -> Result<AppConfig, Box<dyn std::error::Error>> {
    let config_path = get_config_path()?;
    
    if !config_path.exists() {
        // Return default config if file doesn't exist
        let default_config = AppConfig {
            starred_models: HashSet::new(),
            privacy_mode: true,
            encrypt_database: true,
            openwebui_integration: true,
            last_updated: None,
        };
        
        // Save the default config
        save_app_config(&default_config, &default_config.starred_models).await?;
        return Ok(default_config);
    }
    
    let content = fs::read_to_string(&config_path).await?;
    let config: AppConfig = serde_json::from_str(&content)?;
    
    Ok(config)
}

// Save application configuration
pub async fn save_app_config(
    config: &AppConfig, 
    starred_models: &HashSet<String>
) -> Result<(), Box<dyn std::error::Error>> {
    let config_path = get_config_path()?;
    
    let mut updated_config = config.clone();
    updated_config.starred_models = starred_models.clone();
    updated_config.last_updated = Some(chrono::Utc::now().to_rfc3339());
    
    let content = serde_json::to_string_pretty(&updated_config)?;
    fs::write(&config_path, content).await?;
    
    Ok(())
}

// Update specific configuration setting
pub async fn update_config_setting(
    key: &str, 
    value: serde_json::Value
) -> Result<(), Box<dyn std::error::Error>> {
    let mut config = load_app_config().await?;
    
    match key {
        "privacy_mode" => {
            if let Some(val) = value.as_bool() {
                config.privacy_mode = val;
            }
        }
        "encrypt_database" => {
            if let Some(val) = value.as_bool() {
                config.encrypt_database = val;
            }
        }
        "openwebui_integration" => {
            if let Some(val) = value.as_bool() {
                config.openwebui_integration = val;
            }
        }
        _ => return Err(format!("Unknown configuration key: {}", key).into()),
    }
    
    save_app_config(&config, &config.starred_models).await?;
    Ok(())
}

// Get app data directory
pub fn get_app_data_dir() -> Result<PathBuf, Box<dyn std::error::Error>> {
    let home_dir = dirs::home_dir()
        .ok_or("Could not find home directory")?;
    
    let app_dir = home_dir.join(".ollama_model_viewer");
    
    // Create directory if it doesn't exist
    if !app_dir.exists() {
        std::fs::create_dir_all(&app_dir)?;
    }
    
    Ok(app_dir)
}

// Get temporary directory for app operations
pub fn get_temp_dir() -> Result<PathBuf, Box<dyn std::error::Error>> {
    let temp_dir = std::env::temp_dir().join("ollama_model_viewer");
    
    // Create directory if it doesn't exist
    if !temp_dir.exists() {
        std::fs::create_dir_all(&temp_dir)?;
    }
    
    Ok(temp_dir)
} 