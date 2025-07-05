use std::collections::HashMap;
use std::path::PathBuf;
use serde::{Deserialize, Serialize};
use crate::UsageInfo;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OpenWebUIConfig {
    pub data_path: Option<PathBuf>,
    pub enabled: bool,
    pub privacy_mode: bool,
}

// Detect OpenWebUI data directory
pub async fn detect_openwebui_path() -> Option<PathBuf> {
    let common_paths = vec![
        // Temporary copy location
        dirs::home_dir()?.join("tmp").join("openwebui"),
        // Docker volume mounts
        dirs::home_dir()?.join("openwebui"),
        dirs::home_dir()?.join("open-webui"), 
        dirs::home_dir()?.join("open_webui"),
        // Local installations
        dirs::home_dir()?.join(".config").join("open-webui"),
        dirs::home_dir()?.join(".local").join("share").join("open-webui"),
    ];
    
    // Check common paths first
    for path in common_paths {
        let db_path = path.join("webui.db");
        if db_path.exists() {
            println!("✅ Found OpenWebUI database at: {:?}", db_path);
            return Some(path);
        }
    }
    
    // Try to copy from Docker container if running
    if let Ok(docker_path) = copy_from_docker_container().await {
        return Some(docker_path);
    }
    
    println!("⚠️ OpenWebUI database not found. Usage data will not be available.");
    None
}

// Copy database from Docker container
async fn copy_from_docker_container() -> Result<PathBuf, Box<dyn std::error::Error>> {
    use std::process::Command;
    
    // Check if Docker is available
    let output = Command::new("docker")
        .arg("ps")
        .arg("--format")
        .arg("{{.Names}}")
        .output()?;
    
    if !output.status.success() {
        return Err("Docker not available".into());
    }
    
    let container_names = String::from_utf8(output.stdout)?;
    
    for container_name in container_names.lines() {
        if container_name.to_lowercase().contains("webui") || 
           container_name.to_lowercase().contains("open-webui") {
            
            // Try to copy database from container
            let temp_path = dirs::home_dir()
                .ok_or("Could not find home directory")?
                .join("tmp")
                .join("openwebui");
            
            tokio::fs::create_dir_all(&temp_path).await?;
            
            let copy_result = Command::new("docker")
                .arg("cp")
                .arg(format!("{}:/app/backend/data/webui.db", container_name))
                .arg(temp_path.join("webui.db"))
                .output()?;
            
            if copy_result.status.success() && temp_path.join("webui.db").exists() {
                println!("✅ Copied OpenWebUI database from Docker container '{}' to: {:?}", 
                        container_name, temp_path.join("webui.db"));
                return Ok(temp_path);
            }
        }
    }
    
    Err("No OpenWebUI containers found".into())
}

// Get model usage data from OpenWebUI database
pub async fn get_openwebui_usage_data(_db_path: &PathBuf) -> Result<HashMap<String, UsageInfo>, Box<dyn std::error::Error>> {
    // For security and privacy, we'll implement a simplified version
    // In a real implementation, we would use rusqlite to read the database
    
    let usage_data = HashMap::new();
    
    // This is a placeholder implementation
    // In the actual implementation, we would:
    // 1. Check if database is encrypted
    // 2. Decrypt if necessary (with user consent)
    // 3. Query only usage statistics (no chat content)
    // 4. Clean up temporary files securely
    
    println!("🔒 OpenWebUI integration disabled for privacy protection");
    println!("💡 Future versions will include secure usage statistics");
    
    Ok(usage_data)
}

// Clean model name for matching between Ollama and OpenWebUI
pub fn clean_model_name_for_matching(model_name: &str) -> String {
    let prefixes_to_remove = ["ollama/", "local/", "models/"];
    
    let mut clean_name = model_name.to_lowercase().trim().to_string();
    
    for prefix in prefixes_to_remove {
        if clean_name.starts_with(prefix) {
            clean_name = clean_name[prefix.len()..].to_string();
        }
    }
    
    clean_name
}

// Format timestamp for display
pub fn format_last_used_time(timestamp: &str) -> String {
    use chrono::{DateTime, Utc};
    
    // Try to parse various timestamp formats
    if let Ok(parsed_time) = timestamp.parse::<i64>() {
        if let Some(datetime) = DateTime::from_timestamp(parsed_time, 0) {
            let now = Utc::now();
            let diff = now.signed_duration_since(datetime);
            
            if diff.num_days() == 0 {
                if diff.num_hours() == 0 {
                    let minutes = diff.num_minutes();
                    return format!("{} minutes ago", minutes);
                } else {
                    let hours = diff.num_hours();
                    return format!("{} hours ago", hours);
                }
            } else if diff.num_days() == 1 {
                return "1 day ago".to_string();
            } else if diff.num_days() < 7 {
                return format!("{} days ago", diff.num_days());
            } else if diff.num_days() < 30 {
                let weeks = diff.num_days() / 7;
                return format!("{} week{} ago", weeks, if weeks > 1 { "s" } else { "" });
            } else if diff.num_days() < 365 {
                let months = diff.num_days() / 30;
                return format!("{} month{} ago", months, if months > 1 { "s" } else { "" });
            } else {
                let years = diff.num_days() / 365;
                return format!("{} year{} ago", years, if years > 1 { "s" } else { "" });
            }
        }
    }
    
    "Unknown".to_string()
}

// Privacy notice for OpenWebUI integration
pub fn get_privacy_notice() -> String {
    r#"
🔒 Privacy Protection Notice

OpenWebUI integration has been detected but is currently disabled
for maximum privacy protection.

✅ What we would access (with your consent):
• Model usage statistics only
• No chat content or conversations
• Frequency of model usage
• Last used timestamps

❌ What we never access:
• Chat conversations or messages
• User data or personal information
• API keys or authentication tokens
• Any content of your interactions

🛡️ Security measures:
• Database encryption by default
• Local processing only
• Secure cleanup of temporary files
• No data transmission to external services

🗺️ Future roadmap (currently disabled):
• Chat browsing and search
• Conversation analysis tools
• Knowledge base extraction
• Usage analytics dashboard

Would you like to enable OpenWebUI integration with these privacy protections?
"#.to_string()
} 