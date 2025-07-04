/**
 * 🚀 Ollama Model Viewer - Main Frontend Logic
 * A beautiful, ADHD-friendly desktop application for viewing and managing Ollama models
 */

import { invoke } from '@tauri-apps/api/tauri';
import { listen } from '@tauri-apps/api/event';
import { ask, message } from '@tauri-apps/api/dialog';
import { writeText } from '@tauri-apps/api/clipboard';

// Types
interface ModelData {
    name: string;
    id: string;
    size: string;
    modified: string;
    age_category: string;
    capabilities: string[];
    status: string;
    is_liberated: boolean;
    is_starred: boolean;
    is_queued_for_deletion: boolean;
    is_duplicate: boolean;
    is_special_variant: boolean;
    usage_info?: {
        usage_count: number;
        last_used?: string;
        first_used?: string;
        total_tokens?: number;
        average_response_time?: number;
    };
}

// Global state
let allModels: ModelData[] = [];
let filteredModels: ModelData[] = [];
let currentFilter = 'all';
let currentSort = 'name';
let searchQuery = '';

// DOM elements
const loadingEl = document.getElementById('loading') as HTMLElement;
const modelsGridEl = document.getElementById('models-grid') as HTMLElement;
const searchInputEl = document.getElementById('search-input') as HTMLInputElement;
const filterSelectEl = document.getElementById('filter-select') as HTMLSelectElement;
const sortSelectEl = document.getElementById('sort-select') as HTMLSelectElement;
const statusTextEl = document.getElementById('status-text') as HTMLElement;
const modelCountEl = document.getElementById('model-count') as HTMLElement;
const storageInfoEl = document.getElementById('storage-info') as HTMLElement;
const queueBtnEl = document.getElementById('queue-btn') as HTMLButtonElement;
const refreshBtnEl = document.getElementById('refresh-btn') as HTMLButtonElement;
const helpBtnEl = document.getElementById('help-btn') as HTMLButtonElement;

// Initialize the application
async function init() {
    console.log('🚀 Initializing Ollama Model Viewer...');
    
    setupEventListeners();
    await loadModels();
    
    // Listen for backend events
    await listen('model-updated', () => {
        loadModels();
    });
    
    console.log('✅ Application initialized successfully');
}

// Set up event listeners
function setupEventListeners() {
    // Search functionality
    searchInputEl.addEventListener('input', (e) => {
        searchQuery = (e.target as HTMLInputElement).value.toLowerCase();
        filterAndDisplayModels();
    });
    
    // Filter functionality
    filterSelectEl.addEventListener('change', (e) => {
        currentFilter = (e.target as HTMLSelectElement).value;
        filterAndDisplayModels();
    });
    
    // Sort functionality
    sortSelectEl.addEventListener('change', (e) => {
        currentSort = (e.target as HTMLSelectElement).value;
        filterAndDisplayModels();
    });
    
    // Button handlers
    refreshBtnEl.addEventListener('click', loadModels);
    queueBtnEl.addEventListener('click', showDeletionQueue);
    helpBtnEl.addEventListener('click', showHelp);
}

// Load models from backend
async function loadModels() {
    try {
        updateStatus('🔄 Loading models...');
        showLoading(true);
        
        const models = await invoke('get_models') as ModelData[];
        allModels = models;
        
        updateStatus('✅ Models loaded successfully');
        updateModelCount();
        updateStorageInfo();
        filterAndDisplayModels();
        
    } catch (error) {
        console.error('Error loading models:', error);
        updateStatus('❌ Failed to load models');
        await message(`Failed to load models: ${error}`, 'Error');
    } finally {
        showLoading(false);
    }
}

// Filter and display models based on current criteria
function filterAndDisplayModels() {
    // Apply search filter
    let filtered = allModels.filter(model => 
        model.name.toLowerCase().includes(searchQuery) ||
        model.capabilities.some(cap => cap.toLowerCase().includes(searchQuery))
    );
    
    // Apply category filter
    switch (currentFilter) {
        case 'recent':
            filtered = filtered.filter(model => model.age_category === 'recent');
            break;
        case 'moderate':
            filtered = filtered.filter(model => model.age_category === 'moderate');
            break;
        case 'old':
            filtered = filtered.filter(model => model.age_category === 'old');
            break;
        case 'starred':
            filtered = filtered.filter(model => model.is_starred);
            break;
        case 'liberated':
            filtered = filtered.filter(model => model.is_liberated);
            break;
        case 'queued':
            filtered = filtered.filter(model => model.is_queued_for_deletion);
            break;
    }
    
    // Apply sorting
    filtered.sort((a, b) => {
        switch (currentSort) {
            case 'name':
                return a.name.localeCompare(b.name);
            case 'size':
                return parseSize(b.size) - parseSize(a.size);
            case 'modified':
                return new Date(b.modified).getTime() - new Date(a.modified).getTime();
            default:
                return 0;
        }
    });
    
    filteredModels = filtered;
    displayModels();
    updateQueueCount();
}

// Display models in the grid
function displayModels() {
    if (filteredModels.length === 0) {
        modelsGridEl.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: var(--text-secondary);">
                <h3>🔍 No models found</h3>
                <p>Try adjusting your search or filter criteria.</p>
            </div>
        `;
        return;
    }
    
    modelsGridEl.innerHTML = filteredModels.map((model, index) => createModelCard(model, index)).join('');
    
    // Add event listeners to action buttons
    modelsGridEl.querySelectorAll('.action-btn').forEach(btn => {
        btn.addEventListener('click', handleActionClick);
    });
}

// Create a model card HTML
function createModelCard(model: ModelData, index: number): string {
    const ageClass = model.age_category;
    const statusEmojis = [];
    
    if (model.is_starred) statusEmojis.push('⭐');
    if (model.is_liberated) statusEmojis.push('🔓');
    if (model.is_queued_for_deletion) statusEmojis.push('🗑️');
    if (model.is_duplicate) statusEmojis.push('📋');
    if (model.is_special_variant) statusEmojis.push('🎯');
    
    const usageInfo = model.usage_info;
    const usageText = usageInfo ? 
        `📊 Used ${usageInfo.usage_count} times` + 
        (usageInfo.last_used ? `, last used ${formatDate(usageInfo.last_used)}` : '') : 
        '📊 No usage data';
    
    return `
        <div class="model-card ${ageClass} ${model.is_starred ? 'starred' : ''} ${model.is_liberated ? 'liberated' : ''} ${model.is_queued_for_deletion ? 'queued' : ''}" 
             style="animation-delay: ${index * 0.1}s;">
            <div class="model-header">
                <h3 class="model-name">${escapeHtml(model.name)}</h3>
                <div class="model-status">${statusEmojis.join(' ')}</div>
            </div>
            
            <div class="model-info">
                <div class="model-size">
                    <span>💾</span>
                    <span>${model.size}</span>
                </div>
                <div class="model-modified">
                    <span>📅</span>
                    <span>${formatDate(model.modified)}</span>
                </div>
                <div class="model-capabilities">
                    <span>🔧</span>
                    ${model.capabilities.map(cap => `<span class="capability-tag">${escapeHtml(cap)}</span>`).join('')}
                </div>
                <div class="model-usage" style="display: flex; align-items: center; gap: 8px;">
                    <span>${usageText}</span>
                </div>
            </div>
            
            <div class="model-actions">
                <button class="action-btn action-star ${model.is_starred ? 'active' : ''}" 
                        data-action="star" data-model="${model.id}">
                    ${model.is_starred ? '⭐ Starred' : '☆ Star'}
                </button>
                <button class="action-btn action-queue ${model.is_queued_for_deletion ? 'active' : ''}" 
                        data-action="queue" data-model="${model.id}">
                    ${model.is_queued_for_deletion ? '✅ Queued' : '🗑️ Queue'}
                </button>
                <button class="action-btn" data-action="copy" data-model="${model.id}">
                    📋 Copy Name
                </button>
            </div>
        </div>
    `;
}

// Handle action button clicks
async function handleActionClick(event: Event) {
    const target = event.target as HTMLButtonElement;
    const action = target.dataset.action;
    const modelId = target.dataset.model;
    
    if (!action || !modelId) return;
    
    try {
        switch (action) {
            case 'star':
                await invoke('toggle_star', { modelId });
                await loadModels();
                break;
                
            case 'queue':
                await invoke('toggle_deletion_queue', { modelId });
                await loadModels();
                break;
                
            case 'copy':
                const model = allModels.find(m => m.id === modelId);
                if (model) {
                    await writeText(model.name);
                    updateStatus(`📋 Copied "${model.name}" to clipboard`);
                }
                break;
        }
    } catch (error) {
        console.error('Action failed:', error);
        await message(`Action failed: ${error}`, 'Error');
    }
}

// Show/hide loading state
function showLoading(show: boolean) {
    loadingEl.style.display = show ? 'flex' : 'none';
    modelsGridEl.style.display = show ? 'none' : 'grid';
}

// Update status text
function updateStatus(text: string) {
    statusTextEl.textContent = text;
    console.log(text);
}

// Update model count display
function updateModelCount() {
    const total = allModels.length;
    const starred = allModels.filter(m => m.is_starred).length;
    const queued = allModels.filter(m => m.is_queued_for_deletion).length;
    
    modelCountEl.textContent = `📊 ${total} models (⭐ ${starred}, 🗑️ ${queued})`;
}

// Update queue count in button
function updateQueueCount() {
    const queuedCount = allModels.filter(m => m.is_queued_for_deletion).length;
    queueBtnEl.textContent = `🗑️ Queue (${queuedCount})`;
}

// Update storage information
async function updateStorageInfo() {
    try {
        const storageData = await invoke('get_storage_info') as { total: string, ollama: string };
        storageInfoEl.textContent = `💾 Ollama: ${storageData.ollama} / Total: ${storageData.total}`;
    } catch (error) {
        storageInfoEl.textContent = '💾 Storage info unavailable';
    }
}

// Show deletion queue management
async function showDeletionQueue() {
    const queuedModels = allModels.filter(m => m.is_queued_for_deletion);
    
    if (queuedModels.length === 0) {
        await message('No models queued for deletion.', 'Info');
        return;
    }
    
    const modelNames = queuedModels.map(m => m.name).join('\n• ');
    const confirmed = await ask(
        `Execute deletion of ${queuedModels.length} models?\n\n• ${modelNames}`,
        'Confirm Deletion'
    );
    
    if (confirmed) {
        try {
            updateStatus('🗑️ Deleting queued models...');
            await invoke('execute_deletions');
            await loadModels();
            updateStatus('✅ Models deleted successfully');
        } catch (error) {
            await message(`Failed to delete models: ${error}`, 'Error');
        }
    }
}

// Show help dialog
async function showHelp() {
    const helpText = `
🚀 Ollama Model Viewer Help

🔍 Search: Type to search model names and capabilities
🎯 Filter: Choose category (Recent, Old, Starred, etc.)
📊 Sort: Order by name, size, or date

Model Actions:
⭐ Star: Mark important models
🗑️ Queue: Queue for batch deletion
📋 Copy: Copy model name to clipboard

Color Coding:
🟢 Recent models (< 2 weeks)
🟡 Moderate models (2-4 weeks)  
🔴 Old models (1+ month)
🟣 Starred models
🟠 Liberated models

Keyboard Shortcuts:
Ctrl/Cmd + R: Refresh
Ctrl/Cmd + F: Focus search
Escape: Clear search
    `.trim();
    
    await message(helpText, 'Help');
}

// Utility functions
function parseSize(sizeStr: string): number {
    const match = sizeStr.match(/^([\d.]+)\s*(GB|MB|KB|B)?$/i);
    if (!match) return 0;
    
    const num = parseFloat(match[1]);
    const unit = (match[2] || 'B').toUpperCase();
    
    switch (unit) {
        case 'GB': return num * 1024 * 1024 * 1024;
        case 'MB': return num * 1024 * 1024;
        case 'KB': return num * 1024;
        default: return num;
    }
}

function formatDate(dateStr: string): string {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
    if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`;
    return `${Math.floor(diffDays / 365)} years ago`;
}

function escapeHtml(text: string): string {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
        e.preventDefault();
        loadModels();
    } else if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
        e.preventDefault();
        searchInputEl.focus();
        searchInputEl.select();
    } else if (e.key === 'Escape') {
        searchInputEl.value = '';
        searchQuery = '';
        filterAndDisplayModels();
    }
});

// Initialize when the DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
} 