from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.api.api_keys import router as api_keys_router
from app.database.models import DatabaseManager

app = FastAPI(
    title="API Key Manager",
    description="Standalone API Key Management System",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
db_manager = DatabaseManager()

# Include API routers
app.include_router(api_keys_router)

@app.get("/", response_class=HTMLResponse)
async def home():
    """Main page with API key input"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>API Key Manager</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                text-align: center;
                margin-bottom: 30px;
            }
            .api-key-section {
                margin-bottom: 30px;
                padding: 20px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                background-color: #fafafa;
            }
            .form-group {
                margin-bottom: 20px;
            }
            label {
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
                color: #555;
            }
            input[type="text"], input[type="email"], input[type="number"] {
                width: 100%;
                padding: 12px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 16px;
                box-sizing: border-box;
            }
            button {
                background-color: #007bff;
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                margin-right: 10px;
                margin-bottom: 10px;
            }
            button:hover {
                background-color: #0056b3;
            }
            button.danger {
                background-color: #dc3545;
            }
            button.danger:hover {
                background-color: #c82333;
            }
            .status {
                margin-top: 20px;
                padding: 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            .status.success {
                background-color: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }
            .status.error {
                background-color: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }
            .status.info {
                background-color: #d1ecf1;
                color: #0c5460;
                border: 1px solid #bee5eb;
            }
            .key-info {
                background-color: #e9ecef;
                padding: 15px;
                border-radius: 5px;
                margin-top: 15px;
                font-family: monospace;
                font-size: 14px;
            }
            .nav-tabs {
                display: flex;
                border-bottom: 1px solid #ddd;
                margin-bottom: 20px;
            }
            .nav-tab {
                padding: 10px 20px;
                cursor: pointer;
                border: 1px solid transparent;
                border-bottom: none;
                background: none;
                color: #666;
            }
            .nav-tab.active {
                background: white;
                border-color: #ddd;
                color: #333;
                border-bottom: 1px solid white;
                margin-bottom: -1px;
            }
            .tab-content {
                display: none;
            }
            .tab-content.active {
                display: block;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔑 API Key Manager</h1>
            
            <div class="nav-tabs">
                <button class="nav-tab active" onclick="showTab('validate')">Validate Key</button>
                <button class="nav-tab" onclick="showTab('create')">Create Key</button>
                <button class="nav-tab" onclick="showTab('manage')">Manage Keys</button>
            </div>
            
            <!-- Validate Key Tab -->
            <div id="validate" class="tab-content active">
                <div class="api-key-section">
                    <h3>🔍 Validate API Key</h3>
                    <p>Enter your API key to check its status and remaining quota.</p>
                    
                    <div class="form-group">
                        <label for="validateKey">API Key:</label>
                        <input type="text" id="validateKey" placeholder="sk-proj-..." />
                    </div>
                    
                    <button onclick="validateKey()">🔍 Validate Key</button>
                    
                    <div id="validateStatus"></div>
                </div>
            </div>
            
            <!-- Create Key Tab -->
            <div id="create" class="tab-content">
                <div class="api-key-section">
                    <h3>✨ Create New API Key</h3>
                    <p>Generate a new API key for your application.</p>
                    
                    <div class="form-group">
                        <label for="keyName">Key Name:</label>
                        <input type="text" id="keyName" placeholder="e.g., Production App, Test Environment" />
                    </div>
                    
                    <div class="form-group">
                        <label for="userEmail">User Email:</label>
                        <input type="email" id="userEmail" placeholder="user@example.com" />
                    </div>
                    
                    <div class="form-group">
                        <label for="organization">Organization (Optional):</label>
                        <input type="text" id="organization" placeholder="Company Name" />
                    </div>
                    
                    <div class="form-group">
                        <label for="dailyQuota">Daily Quota:</label>
                        <input type="number" id="dailyQuota" value="100" min="1" max="10000" />
                    </div>
                    
                    <div class="form-group">
                        <label for="rateLimit">Rate Limit (requests/min):</label>
                        <input type="number" id="rateLimit" value="60" min="1" max="1000" />
                    </div>
                    
                    <button onclick="createKey()">✨ Create API Key</button>
                    
                    <div id="createStatus"></div>
                </div>
            </div>
            
            <!-- Manage Keys Tab -->
            <div id="manage" class="tab-content">
                <div class="api-key-section">
                    <h3>⚙️ Manage API Keys</h3>
                    <p>View, update, and revoke existing API keys.</p>
                    
                    <button onclick="loadKeys()">📋 Load All Keys</button>
                    <button onclick="refreshKeys()">🔄 Refresh</button>
                    
                    <div id="keysList"></div>
                </div>
            </div>
        </div>

        <script>
            function showTab(tabName) {
                // Hide all tab contents
                const tabContents = document.querySelectorAll('.tab-content');
                tabContents.forEach(tab => tab.classList.remove('active'));
                
                // Remove active class from all tabs
                const tabs = document.querySelectorAll('.nav-tab');
                tabs.forEach(tab => tab.classList.remove('active'));
                
                // Show selected tab content
                document.getElementById(tabName).classList.add('active');
                
                // Add active class to selected tab
                event.target.classList.add('active');
            }
            
            async function validateKey() {
                const apiKey = document.getElementById('validateKey').value.trim();
                const statusDiv = document.getElementById('validateStatus');
                
                if (!apiKey) {
                    statusDiv.innerHTML = '<div class="status error">Please enter an API key</div>';
                    return;
                }
                
                try {
                    const response = await fetch('/api/keys/validate', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ api_key: apiKey })
                    });
                    
                    const data = await response.json();
                    
                    if (data.valid) {
                        let statusClass = 'success';
                        if (data.message.includes('quota exceeded') || data.message.includes('rate limit')) {
                            statusClass = 'warning';
                        }
                        
                        statusDiv.innerHTML = `
                            <div class="status ${statusClass}">
                                <strong>✅ ${data.message}</strong>
                                <div class="key-info">
                                    <strong>Key Name:</strong> ${data.key_info.name}<br>
                                    <strong>User:</strong> ${data.key_info.user_email}<br>
                                    <strong>Organization:</strong> ${data.key_info.organization || 'N/A'}<br>
                                    <strong>Status:</strong> ${data.key_info.status}<br>
                                    <strong>Remaining Daily Quota:</strong> ${data.remaining_quota || 'N/A'}<br>
                                    <strong>Rate Limit:</strong> ${data.rate_limit_remaining || 'N/A'} requests/min<br>
                                    <strong>Created:</strong> ${new Date(data.key_info.created_at).toLocaleString()}<br>
                                    <strong>Last Used:</strong> ${data.key_info.last_used ? new Date(data.key_info.last_used).toLocaleString() : 'Never'}
                                </div>
                            </div>
                        `;
                    } else {
                        statusDiv.innerHTML = `<div class="status error">❌ ${data.message}</div>`;
                    }
                } catch (error) {
                    statusDiv.innerHTML = `<div class="status error">❌ Error: ${error.message}</div>`;
                }
            }
            
            async function createKey() {
                const keyName = document.getElementById('keyName').value.trim();
                const userEmail = document.getElementById('userEmail').value.trim();
                const organization = document.getElementById('organization').value.trim();
                const dailyQuota = parseInt(document.getElementById('dailyQuota').value);
                const rateLimit = parseInt(document.getElementById('rateLimit').value);
                const statusDiv = document.getElementById('createStatus');
                
                if (!keyName || !userEmail) {
                    statusDiv.innerHTML = '<div class="status error">Please fill in all required fields</div>';
                    return;
                }
                
                try {
                    const response = await fetch('/api/keys/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            name: keyName,
                            user_email: userEmail,
                            organization: organization || null,
                            daily_quota: dailyQuota,
                            rate_limit: rateLimit
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        statusDiv.innerHTML = `
                            <div class="status success">
                                <strong>🎉 API Key Created Successfully!</strong><br>
                                <strong>API Key:</strong> ${data.api_key}<br>
                                <strong>⚠️ IMPORTANT:</strong> Save this key securely. It won't be shown again!
                            </div>
                        `;
                        
                        // Clear form
                        document.getElementById('keyName').value = '';
                        document.getElementById('userEmail').value = '';
                        document.getElementById('organization').value = '';
                    } else {
                        statusDiv.innerHTML = `<div class="status error">❌ Error: ${data.detail}</div>`;
                    }
                } catch (error) {
                    statusDiv.innerHTML = `<div class="status error">❌ Error: ${error.message}</div>`;
                }
            }
            
            async function loadKeys() {
                const keysListDiv = document.getElementById('keysList');
                
                try {
                    const response = await fetch('/api/keys/');
                    const data = await response.json();
                    
                    if (response.ok && data.api_keys.length > 0) {
                        let html = '<h4>📋 API Keys List</h4>';
                        
                        data.api_keys.forEach(key => {
                            const statusClass = key.status === 'active' ? 'success' : 'error';
                            const statusIcon = key.status === 'active' ? '✅' : '❌';
                            
                            html += `
                                <div class="key-info" style="margin-bottom: 15px;">
                                    <strong>${statusIcon} ${key.name}</strong> (${key.status})<br>
                                    <strong>Key:</strong> ${key.key_prefix}<br>
                                    <strong>User:</strong> ${key.user_email}<br>
                                    <strong>Organization:</strong> ${key.organization || 'N/A'}<br>
                                    <strong>Daily Quota:</strong> ${key.current_daily_usage}/${key.daily_quota}<br>
                                    <strong>Rate Limit:</strong> ${key.rate_limit}/min<br>
                                    <strong>Created:</strong> ${new Date(key.created_at).toLocaleString()}<br>
                                    <strong>Last Used:</strong> ${key.last_used ? new Date(key.last_used).toLocaleString() : 'Never'}<br>
                                    <button onclick="revokeKey(${key.id})" class="danger" ${key.status !== 'active' ? 'disabled' : ''}>
                                        ${key.status === 'active' ? '🚫 Revoke' : 'Already Revoked'}
                                    </button>
                                    <button onclick="deleteKey(${key.id})" class="danger">🗑️ Delete</button>
                                </div>
                            `;
                        });
                        
                        keysListDiv.innerHTML = html;
                    } else {
                        keysListDiv.innerHTML = '<div class="status info">No API keys found</div>';
                    }
                } catch (error) {
                    keysListDiv.innerHTML = `<div class="status error">❌ Error: ${error.message}</div>`;
                }
            }
            
            async function revokeKey(keyId) {
                if (!confirm('Are you sure you want to revoke this API key?')) {
                    return;
                }
                
                try {
                    const response = await fetch(`/api/keys/${keyId}/revoke`, {
                        method: 'POST'
                    });
                    
                    if (response.ok) {
                        alert('API key revoked successfully!');
                        loadKeys(); // Refresh the list
                    } else {
                        const data = await response.json();
                        alert(`Error: ${data.detail}`);
                    }
                } catch (error) {
                    alert(`Error: ${error.message}`);
                }
            }
            
            async function deleteKey(keyId) {
                if (!confirm('Are you sure you want to permanently delete this API key? This action cannot be undone!')) {
                    return;
                }
                
                try {
                    const response = await fetch(`/api/keys/${keyId}`, {
                        method: 'DELETE'
                    });
                    
                    if (response.ok) {
                        alert('API key deleted successfully!');
                        loadKeys(); // Refresh the list
                    } else {
                        const data = await response.json();
                        alert(`Error: ${data.detail}`);
                    }
                } catch (error) {
                    alert(`Error: ${error.message}`);
                }
            }
            
            function refreshKeys() {
                loadKeys();
            }
        </script>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "API Key Manager"}

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8004))
    uvicorn.run(app, host="0.0.0.0", port=port)
