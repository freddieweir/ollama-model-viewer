use std::process::Command;
use serde::{Deserialize, Serialize};
use crate::{ModelData, UsageInfo};

// Liberation detection keywords
const LIBERATION_KEYWORDS: &[&str] = &[
    "uncensored", "abliterated", "art", "unfiltered", "raw", 
    "nsfw", "freedom", "libre", "unleashed", "unlimited",
    "dpo", "rogue", "wild", "rebel", "free"
];

// Special parameter suffixes that are meaningful variants (not duplicates)
const SPECIAL_SUFFIXES: &[&str] = &[
    "instruct", "chat", "code", "vision", "embed", "text",
    "a3b", "dpo", "ift", "sft", "rlhf", "tool", "function",
    "reasoning", "uncensored", "abliterated", "art", "base"
];

// Get models from Ollama
pub async fn get_ollama_models() -> Result<Vec<ModelData>, String> {
    let output = Command::new("ollama")
        .arg("list")
        .output()
        .map_err(|e| format!("Failed to execute ollama command: {}", e))?;

    if !output.status.success() {
        return Err("Ollama command failed. Is Ollama running?".to_string());
    }

    let stdout = String::from_utf8(output.stdout)
        .map_err(|e| format!("Failed to parse ollama output: {}", e))?;

    parse_ollama_output(&stdout)
}

// Parse ollama list output
fn parse_ollama_output(output: &str) -> Result<Vec<ModelData>, String> {
    let lines: Vec<&str> = output.lines().collect();
    
    if lines.is_empty() {
        return Ok(Vec::new());
    }

    // Skip header line
    let data_lines = &lines[1..];
    let mut models = Vec::new();

    for line in data_lines {
        if line.trim().is_empty() {
            continue;
        }

        let parts: Vec<&str> = line.split_whitespace().collect();
        if parts.len() >= 4 {
            let name = parts[0].to_string();
            let id = parts[1].to_string();
            let size = format!("{} {}", parts[2], parts[3]);
            let modified = parts[4..].join(" ");

            // Determine age category and color
            let age_category = get_age_category(&modified);
            
            // Determine capabilities based on model name
            let capabilities = determine_capabilities(&name);
            
            // Check if model is liberated/uncensored
            let is_liberated = is_liberated_model(&name);
            
            // Check for duplicates and variants
            let (is_duplicate, is_special_variant) = analyze_model_variants(&name, &models);

            let model_data = ModelData {
                name,
                id,
                size,
                modified,
                age_category,
                capabilities,
                status: "🟢 Available".to_string(),
                is_liberated,
                is_starred: false, // Will be set later based on config
                is_queued_for_deletion: false, // Will be set later
                is_duplicate,
                is_special_variant,
                usage_info: None, // Will be populated from OpenWebUI if available
            };

            models.push(model_data);
        }
    }

    Ok(models)
}

// Determine age category based on modified time
fn get_age_category(modified_str: &str) -> String {
    if modified_str.contains("day") {
        if let Some(days_str) = modified_str.split_whitespace().next() {
            if let Ok(days) = days_str.parse::<i32>() {
                return if days <= 14 {
                    "Recently Used".to_string()
                } else if days <= 28 {
                    "Moderately Used".to_string()
                } else {
                    "Old Model".to_string()
                };
            }
        }
    } else if modified_str.contains("week") {
        if let Some(weeks_str) = modified_str.split_whitespace().next() {
            if let Ok(weeks) = weeks_str.parse::<i32>() {
                return if weeks <= 2 {
                    "Recently Used".to_string()
                } else if weeks <= 4 {
                    "Moderately Used".to_string()
                } else {
                    "Old Model".to_string()
                };
            }
        }
    } else if modified_str.contains("month") {
        return "Old Model".to_string();
    }

    "Recently Used".to_string() // Default for unclear time formats
}

// Determine model capabilities based on name
fn determine_capabilities(model_name: &str) -> Vec<String> {
    let mut capabilities = vec!["📝 Text".to_string()];
    let name_lower = model_name.to_lowercase();

    // Vision capabilities
    if ["vision", "vl", "visual", "llava", "clip"].iter().any(|&keyword| name_lower.contains(keyword)) {
        capabilities.push("👁️ Vision".to_string());
    }

    // Code capabilities
    if ["code", "coder", "coding"].iter().any(|&keyword| name_lower.contains(keyword)) {
        capabilities.push("💻 Code".to_string());
    }

    // Embedding capabilities
    if name_lower.contains("embed") {
        capabilities.push("🔗 Embed".to_string());
    }

    // Tool use capabilities
    if ["tool", "function", "agent"].iter().any(|&keyword| name_lower.contains(keyword)) {
        capabilities.push("🛠️ Tools".to_string());
    }

    // Reasoning capabilities
    if ["r1", "reasoning", "think"].iter().any(|&keyword| name_lower.contains(keyword)) {
        capabilities.push("🧠 Reasoning".to_string());
    }

    capabilities
}

// Check if model is liberated/uncensored
fn is_liberated_model(model_name: &str) -> bool {
    let name_lower = model_name.to_lowercase();
    LIBERATION_KEYWORDS.iter().any(|&keyword| name_lower.contains(keyword))
}

// Analyze model variants and duplicates
fn analyze_model_variants(model_name: &str, existing_models: &[ModelData]) -> (bool, bool) {
    let base_name = get_model_base_name(model_name);
    let _params = get_model_params(model_name);
    
    // Check if this is a special variant
    let is_special_variant = is_special_variant(model_name);
    
    // Check for duplicates
    let mut is_duplicate = false;
    
    for existing_model in existing_models {
        let existing_base = get_model_base_name(&existing_model.name);
        let _existing_params = get_model_params(&existing_model.name);
        
        if base_name == existing_base {
            // Same base model
            if !is_special_variant && !existing_model.is_special_variant {
                // Both are regular variants, this is a duplicate
                is_duplicate = true;
                break;
            }
        }
    }
    
    (is_duplicate, is_special_variant)
}

// Get base model name without parameters
fn get_model_base_name(model_name: &str) -> String {
    if let Some(colon_pos) = model_name.find(':') {
        model_name[..colon_pos].to_lowercase()
    } else {
        model_name.to_lowercase()
    }
}

// Get model parameters
fn get_model_params(model_name: &str) -> String {
    if let Some(colon_pos) = model_name.find(':') {
        model_name[colon_pos + 1..].to_lowercase()
    } else {
        String::new()
    }
}

// Check if model has special parameter suffixes
fn is_special_variant(model_name: &str) -> bool {
    let params = get_model_params(model_name);
    if params.is_empty() {
        return false;
    }
    
    SPECIAL_SUFFIXES.iter().any(|&suffix| params.contains(suffix))
}

// Get detailed model information
pub async fn get_ollama_model_details(model_name: &str) -> Result<String, String> {
    let output = Command::new("ollama")
        .arg("show")
        .arg(model_name)
        .output()
        .map_err(|e| format!("Failed to execute ollama show command: {}", e))?;

    if !output.status.success() {
        return Err(format!("Failed to get details for model: {}", model_name));
    }

    let stdout = String::from_utf8(output.stdout)
        .map_err(|e| format!("Failed to parse ollama show output: {}", e))?;

    Ok(stdout)
}

// Delete a model from Ollama
pub async fn delete_ollama_model(model_name: &str) -> Result<(), String> {
    let output = Command::new("ollama")
        .arg("rm")
        .arg(model_name)
        .output()
        .map_err(|e| format!("Failed to execute ollama rm command: {}", e))?;

    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        return Err(format!("Failed to delete model {}: {}", model_name, stderr));
    }

    Ok(())
}

// Check if Ollama is available
pub async fn check_ollama_available() -> bool {
    Command::new("ollama")
        .arg("--version")
        .output()
        .map(|output| output.status.success())
        .unwrap_or(false)
} 