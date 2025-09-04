from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.api.api_keys import router as api_keys_router
from app.api.virtual_staging import router as virtual_staging_router
from app.middleware.auth import verify_admin_credentials
from app.database.models import DatabaseManager

app = FastAPI(
    title="Virtual Staging API",
    description="API Key Management and Virtual Staging System",
    version="1.0.0"
)

# Add CORS middleware - cross origin resource sharing (CORS) to allow requests from any origin
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
app.include_router(api_keys_router, prefix="/admin", tags=["admin"])
app.include_router(virtual_staging_router, prefix="/api", tags=["virtual-staging"])

@app.get("/", response_class=HTMLResponse)
async def home():
    """Main page with Virtual Staging functionality"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Virtual Staging API</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            h1 {
                color: #333;
                text-align: center;
                margin-bottom: 30px;
            }
            .section {
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
            input[type="text"], input[type="email"], input[type="number"], input[type="file"], select {
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
            button.success {
                background-color: #28a745;
            }
            button.success:hover {
                background-color: #218838;
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
                font-size: 16px;
            }
            .nav-tab.active {
                background: white;
                border-color: #ddd;
                color: #333;
                border-bottom: 1px solid white;
                margin-bottom: -1px;
            }
            .admin-link {
                text-decoration: none;
                color: #666 !important;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
            }
            .admin-link:hover {
                color: #495057 !important;
                background-color: #e9ecef;
            }
            .tab-content {
                display: none;
            }
            .tab-content.active {
                display: block;
            }
            .image-preview {
                max-width: 300px;
                max-height: 300px;
                margin: 10px 0;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            .result-gallery {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }
            .result-item {
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 15px;
                background: white;
                text-align: center;
            }
            .result-image {
                max-width: 100%;
                height: auto;
                border-radius: 5px;
                margin-bottom: 10px;
            }
            .loading {
                display: none;
                text-align: center;
                margin: 20px 0;
            }
            .spinner {
                border: 4px solid #f3f3f3;
                border-top: 4px solid #3498db;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 2s linear infinite;
                margin: 0 auto;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            /* API Key Validation Styles */
            .api-key-status {
                margin-top: 10px;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                min-height: 20px;
            }
            .api-key-status.validating {
                background-color: #fff3cd;
                color: #856404;
                border: 1px solid #ffeaa7;
            }
            .api-key-status.valid {
                background-color: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }
            .api-key-status.invalid {
                background-color: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }
            .api-key-input.valid {
                border-color: #28a745;
                background-color: #f8fff9;
            }
            .api-key-input.invalid {
                border-color: #dc3545;
                background-color: #fff8f8;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎨 Virtual Staging API</h1>
            <p style="text-align: center; color: #666;">Transform empty rooms into beautifully furnished spaces with AI</p>
            
            <div class="nav-tabs">
                <button class="nav-tab active" onclick="showTab('virtual-staging')">🎨 Virtual Staging</button>
                <a href="/admin" class="nav-tab admin-link">🔧 Admin Login</a>
            </div>
            
            <!-- Virtual Staging Tab -->
            <div id="virtual-staging" class="tab-content active">
                <!-- API Key Validation Section -->
                <div class="section">
                    <h3>🔐 API Key Authentication</h3>
                    <p>Enter your API key to access the virtual staging features.</p>
                    
                    <div class="form-group">
                        <label for="apiKey">API Key:</label>
                        <input type="password" id="apiKey" placeholder="sk-proj-..." onkeyup="validateAPIKey()" />
                        <div id="apiKeyStatus" class="api-key-status"></div>
                    </div>
                </div>
                
                <!-- Virtual Staging Form (Initially Hidden) -->
                <div id="virtualStagingForm" class="section" style="display: none;">
                    <h3>🏠 Generate Virtual Staging</h3>
                    <p>Upload an image of an empty room and transform it into a beautifully furnished space.</p>
                    
                    <div class="form-group">
                        <label for="imageFile">Room Image:</label>
                        <input type="file" id="imageFile" accept="image/*" onchange="previewImage()" />
                        <img id="imagePreview" class="image-preview" style="display: none;" />
                    </div>
                    
                    <div class="form-group">
                        <label for="numImages">Number of Variations:</label>
                        <select id="numImages">
                            <option value="1">1 image</option>
                            <option value="2">2 images</option>
                            <option value="3" selected>3 images</option>
                            <option value="4">4 images</option>
                            <option value="5">5 images</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="style">Furnishing Style:</label>
                        <select id="style">
                            <option value="scandinavian" selected>Scandinavian</option>
                        </select>
                        <small style="color: #666;">More styles coming soon!</small>
                    </div>
                    
                    <button onclick="generateVirtualStaging()" class="success">🎨 Generate Virtual Staging</button>
                    
                    <div class="loading" id="loading">
                        <div class="spinner"></div>
                        <p>Generating your virtual staging... This may take a few minutes.</p>
                    </div>
                    
                    <div id="stagingResults"></div>
                </div>
            </div>
        </div>
        
        <script>
            // Tab switching for main navigation
            function showTab(tabName) {
                // This function is simplified since we only have virtual staging now
                // Admin is accessed via separate page
            }
            
            // API Key Validation
            let apiKeyValidationTimeout;
            let currentApiKey = '';
            
            function validateAPIKey() {
                const apiKeyInput = document.getElementById('apiKey');
                const apiKeyStatus = document.getElementById('apiKeyStatus');
                const virtualStagingForm = document.getElementById('virtualStagingForm');
                const apiKey = apiKeyInput.value.trim();
                
                // Clear previous timeout
                clearTimeout(apiKeyValidationTimeout);
                
                // Reset styles
                apiKeyInput.classList.remove('api-key-input', 'valid', 'invalid');
                
                if (!apiKey) {
                    apiKeyStatus.className = 'api-key-status';
                    apiKeyStatus.innerHTML = '';
                    virtualStagingForm.style.display = 'none';
                    currentApiKey = '';
                    return;
                }
                
                // Show validating status
                apiKeyStatus.className = 'api-key-status validating';
                apiKeyStatus.innerHTML = '🔄 Validating API key...';
                
                // Debounced validation (500ms)
                apiKeyValidationTimeout = setTimeout(async () => {
                    try {
                        const response = await fetch('/admin/api/keys/validate', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({ api_key: apiKey }),
                            credentials: 'include'
                        });
                        
                        const data = await response.json();
                        
                        if (data.valid) {
                            // Valid API key
                            apiKeyInput.classList.add('api-key-input', 'valid');
                            apiKeyStatus.className = 'api-key-status valid';
                            apiKeyStatus.innerHTML = `✅ Valid API key! User: ${data.key_info?.user_email || 'Unknown'}`;
                            virtualStagingForm.style.display = 'block';
                            currentApiKey = apiKey;
                            
                            // Add quota info if available
                            if (data.key_info?.daily_quota && data.key_info?.current_daily_usage !== undefined) {
                                const remaining = data.key_info.daily_quota - data.key_info.current_daily_usage;
                                apiKeyStatus.innerHTML += `<br>📊 Quota: ${remaining}/${data.key_info.daily_quota} remaining`;
                            }
                        } else {
                            // Invalid API key
                            apiKeyInput.classList.add('api-key-input', 'invalid');
                            apiKeyStatus.className = 'api-key-status invalid';
                            apiKeyStatus.innerHTML = `❌ ${data.message || 'Invalid API key'}`;
                            virtualStagingForm.style.display = 'none';
                            currentApiKey = '';
                        }
                    } catch (error) {
                        console.error('API key validation error:', error);
                        apiKeyInput.classList.add('api-key-input', 'invalid');
                        apiKeyStatus.className = 'api-key-status invalid';
                        apiKeyStatus.innerHTML = '❌ Unable to validate API key. Please try again.';
                        virtualStagingForm.style.display = 'none';
                        currentApiKey = '';
                    }
                }, 500);
            }
        </script>
        
        <!-- Admin Panel Section (when accessed directly) -->
        <div id="admin-content" style="display: none;">
            <div class="container">
                <div class="section">
                    <h3>🔑 API Key Management</h3>
                    <p>Manage API keys for authentication and usage tracking.</p>
                    
                    <div class="nav-tabs" style="border-bottom: 1px solid #eee; margin-bottom: 15px;">
                        <button class="nav-tab active" onclick="showAdminTab('validate')">Validate Key</button>
                        <button class="nav-tab" onclick="showAdminTab('create')">Create Key</button>
                        <button class="nav-tab" onclick="showAdminTab('manage')">Manage Keys</button>
                    </div>
                    
                    <!-- Validate Key Sub-tab -->
                    <div id="admin-validate" class="tab-content active">
                        <h4>🔍 Validate API Key</h4>
                        <div class="form-group">
                            <label for="validateKey">API Key:</label>
                            <input type="text" id="validateKey" placeholder="sk-proj-..." />
                        </div>
                        <button onclick="validateKey()">🔍 Validate Key</button>
                        <div id="validateStatus"></div>
                    </div>
                    
                    <!-- Create Key Sub-tab -->
                    <div id="admin-create" class="tab-content">
                        <h4>✨ Create New API Key</h4>
                        <div class="form-group">
                            <label for="keyName">Key Name:</label>
                            <input type="text" id="keyName" placeholder="e.g., Production App" />
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
                    
                    <!-- Manage Keys Sub-tab -->
                    <div id="admin-manage" class="tab-content">
                        <h4>⚙️ Manage API Keys</h4>
                        <button onclick="loadKeys()">📋 Load All Keys</button>
                        <button onclick="refreshKeys()">🔄 Refresh</button>
                        <div id="keysList"></div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            function showTab(tabName) {
                // Hide all main tab contents
                const tabContents = document.querySelectorAll('.container > .tab-content');
                tabContents.forEach(tab => tab.classList.remove('active'));
                
                // Remove active class from all main tabs
                const tabs = document.querySelectorAll('.container > .nav-tabs .nav-tab');
                tabs.forEach(tab => tab.classList.remove('active'));
                
                // Show selected tab content
                document.getElementById(tabName).classList.add('active');
                
                // Add active class to selected tab
                event.target.classList.add('active');
            }
            
            function showAdminTab(tabName) {
                // Hide all admin sub-tab contents
                const tabContents = document.querySelectorAll('#admin .tab-content');
                tabContents.forEach(tab => tab.classList.remove('active'));
                
                // Remove active class from all admin tabs
                const tabs = document.querySelectorAll('#admin .nav-tab');
                tabs.forEach(tab => tab.classList.remove('active'));
                
                // Show selected tab content
                document.getElementById('admin-' + tabName).classList.add('active');
                
                // Add active class to selected tab
                event.target.classList.add('active');
            }
            
            function previewImage() {
                const file = document.getElementById('imageFile').files[0];
                const preview = document.getElementById('imagePreview');
                
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        preview.src = e.target.result;
                        preview.style.display = 'block';
                    };
                    reader.readAsDataURL(file);
                } else {
                    preview.style.display = 'none';
                }
            }
            
            async function generateVirtualStaging() {
                console.log('🎯 Generate button clicked!');
                
                // Check if API key is validated
                if (!currentApiKey) {
                    alert('Please enter and validate your API key first.');
                    return;
                }
                
                const fileInput = document.getElementById('imageFile');
                const numImages = document.getElementById('numImages').value;
                const style = document.getElementById('style').value;
                const resultsDiv = document.getElementById('stagingResults');
                const loadingDiv = document.getElementById('loading');
                
                console.log('🔑 Using API key:', currentApiKey.substring(0, 10) + '...');
                console.log('📁 File input:', fileInput);
                console.log('🔢 Num images:', numImages);
                console.log('🎨 Style:', style);
                
                if (!fileInput.files[0]) {
                    console.log('❌ No file selected');
                    resultsDiv.innerHTML = '<div class="status error">Please select an image file</div>';
                    return;
                }
                
                console.log('✅ File selected:', fileInput.files[0].name);
                console.log('✅ File selected:', fileInput.files[0].name);
                
                // Show loading
                console.log('🔄 Showing loading...');
                loadingDiv.style.display = 'block';
                resultsDiv.innerHTML = '';
                
                // Prepare form data
                const formData = new FormData();
                formData.append('image_file', fileInput.files[0]);
                formData.append('num_images', numImages);
                formData.append('style', style);
                
                console.log('📤 Sending request to /api/virtual-staging with API key...');
                console.log('🔑 API Key:', currentApiKey.substring(0, 10) + '...');
                
                try {
                    const response = await fetch('/api/virtual-staging', {
                        method: 'POST',
                        headers: {
                            'X-API-Key': currentApiKey
                        },
                        body: formData
                    });
                    
                    console.log('📥 Response status:', response.status);
                    
                    // Handle API key authentication errors
                    if (response.status === 401) {
                        loadingDiv.style.display = 'none';
                        resultsDiv.innerHTML = `<div class="status error">❌ API Key Authentication Failed: Please check your API key and try again.</div>`;
                        return;
                    }
                    
                    if (!response.ok) {
                        const errorData = await response.json().catch(() => ({}));
                        throw new Error(errorData.detail || `HTTP ${response.status}: Request failed`);
                    }
                    
                    const data = await response.json();
                    console.log('📊 Response data:', data);
                    loadingDiv.style.display = 'none';
                    
                    if (data.success) {
                        let html = `
                            <div class="status success">
                                <strong>🎉 Virtual Staging Complete!</strong><br>
                                Generated ${data.results.length} variations in ${data.metadata.style} style.
                            </div>
                            <div class="result-gallery">
                        `;
                        
                        data.results.forEach((result, index) => {
                            html += `
                                <div class="result-item">
                                    <img src="${result.image}" class="result-image" alt="Generated ${index + 1}" />
                                    <p><strong>Variation ${result.index}</strong></p>
                                    <p>Style: ${result.style}</p>
                                    <p>Seed: ${result.seed}</p>
                                    <button onclick="downloadImage('${result.image}', 'virtual-staging-${index + 1}.png')">⬇️ Download</button>
                                </div>
                            `;
                        });
                        
                        html += '</div>';
                        resultsDiv.innerHTML = html;
                    } else {
                        resultsDiv.innerHTML = `<div class="status error">❌ Error: ${data.detail || 'Unknown error'}</div>`;
                    }
                } catch (error) {
                    console.error('❌ Error occurred:', error);
                    loadingDiv.style.display = 'none';
                    resultsDiv.innerHTML = `<div class="status error">❌ Error: ${error.message}</div>`;
                }
            }
            
            function downloadImage(dataUrl, filename) {
                const link = document.createElement('a');
                link.href = dataUrl;
                link.download = filename;
                link.click();
            }
            
            // Admin functions (keeping existing ones)
            async function validateKey() {
                const apiKey = document.getElementById('validateKey').value.trim();
                const statusDiv = document.getElementById('validateStatus');
                
                if (!apiKey) {
                    statusDiv.innerHTML = '<div class="status error">Please enter an API key</div>';
                    return;
                }
                
                try {
                    const response = await fetch('/admin/api/keys/validate', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ api_key: apiKey })
                    });
                    
                    const data = await response.json();
                    
                    if (data.valid) {
                        statusDiv.innerHTML = `
                            <div class="status success">
                                <strong>✅ ${data.message}</strong><br>
                                <strong>User:</strong> ${data.key_info.user_email}<br>
                                <strong>Status:</strong> ${data.key_info.status}<br>
                                <strong>Remaining Quota:</strong> ${data.remaining_quota || 'N/A'}
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
                    const response = await fetch('/admin/api/keys/', {
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
                                <strong>🎉 API Key Created!</strong><br>
                                <strong>Key:</strong> ${data.api_key}
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
                    const response = await fetch('/admin/api/keys/');
                    const data = await response.json();
                    
                    if (response.ok && data.api_keys.length > 0) {
                        let html = '<h5>📋 API Keys List</h5>';
                        
                        data.api_keys.forEach(key => {
                            const statusIcon = key.status === 'active' ? '✅' : '❌';
                            
                            html += `
                                <div class="status info" style="margin-bottom: 15px;">
                                    <strong>${statusIcon} ${key.name}</strong><br>
                                    <strong>User:</strong> ${key.user_email}<br>
                                    <strong>Status:</strong> ${key.status}<br>
                                    <strong>Usage:</strong> ${key.current_daily_usage}/${key.daily_quota}<br>
                                    <button onclick="revokeKey(${key.id})" class="danger" ${key.status !== 'active' ? 'disabled' : ''}>
                                        ${key.status === 'active' ? '🚫 Revoke' : 'Revoked'}
                                    </button>
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
                if (!confirm('Revoke this API key?')) return;
                
                try {
                    const response = await fetch(`/admin/api/keys/${keyId}/revoke`, {
                        method: 'POST'
                    });
                    
                    if (response.ok) {
                        alert('API key revoked!');
                        loadKeys();
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

@app.get("/test", response_class=HTMLResponse)
async def test_page():
    """Simple test page for virtual staging"""
    with open("test_frontend.html", "r") as f:
        return f.read()

@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(admin_user: str = Depends(verify_admin_credentials)):
    """Protected admin panel for API key management"""
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Admin Panel - Virtual Staging API</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
                position: relative;
            }}
            .container {{
                background: white;
                border-radius: 10px;
                padding: 30px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }}
            .admin-header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                text-align: center;
                position: relative;
            }}
            .back-link {{
                position: absolute;
                top: 15px;
                left: 15px;
                background: rgba(255,255,255,0.2);
                color: white;
                padding: 8px 12px;
                text-decoration: none;
                border-radius: 5px;
                font-size: 14px;
            }}
            .back-link:hover {{
                background: rgba(255,255,255,0.3);
                color: white;
            }}
            h1 {{ color: white; margin-bottom: 10px; }}
            h3 {{ color: #555; }}
            .nav-tabs {{
                border-bottom: 2px solid #eee;
                margin-bottom: 20px;
                display: flex;
                gap: 0;
            }}
            .nav-tab {{
                padding: 12px 24px;
                cursor: pointer;
                border: 1px solid transparent;
                border-bottom: none;
                background: none;
                color: #666;
                font-size: 16px;
            }}
            .nav-tab.active {{
                background: white;
                border-color: #ddd;
                color: #333;
                border-bottom: 1px solid white;
                margin-bottom: -1px;
            }}
            .tab-content {{ display: none; }}
            .tab-content.active {{ display: block; }}
            .form-group {{ margin-bottom: 15px; }}
            .form-group label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
            .form-group input, .form-group select {{
                width: 100%;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 16px;
                box-sizing: border-box;
            }}
            button {{
                background-color: #007bff;
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                margin-right: 10px;
                margin-bottom: 10px;
            }}
            button:hover {{ background-color: #0056b3; }}
            button.success {{ background-color: #28a745; }}
            button.danger {{ background-color: #dc3545; }}
            .status {{ padding: 10px; border-radius: 5px; margin: 10px 0; }}
            .status.success {{ background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
            .status.error {{ background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
            th, td {{ padding: 10px; text-align: left; border: 1px solid #ddd; }}
            th {{ background-color: #f8f9fa; }}
        </style>
    </head>
    <body>
        <div class="admin-header">
            <a href="/" class="back-link">← Back to Virtual Staging</a>
            <h1>🔧 Admin Panel</h1>
            <p>Logged in as: <strong>{admin_user}</strong></p>
            <p>API Key Management & Administration</p>
        </div>
        
        <div class="container">
            <div class="nav-tabs">
                <button class="nav-tab active" onclick="showAdminTab('validate')">Validate Key</button>
                <button class="nav-tab" onclick="showAdminTab('create')">Create Key</button>
                <button class="nav-tab" onclick="showAdminTab('manage')">Manage Keys</button>
            </div>
            
            <!-- Validate Key Tab -->
            <div id="admin-validate" class="tab-content active">
                <h3>🔍 Validate API Key</h3>
                <div class="form-group">
                    <label for="validateKey">API Key:</label>
                    <input type="text" id="validateKey" placeholder="sk-proj-...">
                </div>
                <button onclick="validateKey()">🔍 Validate Key</button>
                <div id="validateStatus"></div>
            </div>
            
            <!-- Create Key Tab -->
            <div id="admin-create" class="tab-content">
                <h3>➕ Create New API Key</h3>
                <div class="form-group">
                    <label for="keyName">Key Name *:</label>
                    <input type="text" id="keyName" placeholder="e.g., production-app">
                </div>
                <div class="form-group">
                    <label for="userEmail">User Email *:</label>
                    <input type="email" id="userEmail" placeholder="user@example.com">
                </div>
                <div class="form-group">
                    <label for="organization">Organization:</label>
                    <input type="text" id="organization" placeholder="Company Name (optional)">
                </div>
                <button onclick="createKey()">➕ Create API Key</button>
                <div id="createStatus"></div>
            </div>
            
            <!-- Manage Keys Tab -->
            <div id="admin-manage" class="tab-content">
                <h3>📋 Manage API Keys</h3>
                <button onclick="loadKeys()">🔄 Refresh Keys</button>
                <div id="keysList"></div>
            </div>
        </div>
        
        <script>
            function showAdminTab(tabName) {{
                const tabs = document.querySelectorAll('.nav-tab');
                const contents = document.querySelectorAll('.tab-content');
                
                tabs.forEach(tab => tab.classList.remove('active'));
                contents.forEach(content => content.classList.remove('active'));
                
                event.target.classList.add('active');
                document.getElementById('admin-' + tabName).classList.add('active');
            }}
            
            async function validateKey() {{
                const key = document.getElementById('validateKey').value.trim();
                const statusDiv = document.getElementById('validateStatus');
                
                if (!key) {{
                    statusDiv.innerHTML = '<div class="status error">Please enter an API key</div>';
                    return;
                }}
                
                try {{
                    const response = await fetch('/admin/api/keys/validate', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ api_key: key }})
                    }});
                    
                    const data = await response.json();
                    
                    if (data.valid) {{
                        statusDiv.innerHTML = `
                            <div class="status success">
                                ✅ Valid API Key<br>
                                <strong>User:</strong> ${{data.key_info.user_email}}<br>
                                <strong>Organization:</strong> ${{data.key_info.organization || 'None'}}<br>
                                <strong>Status:</strong> ${{data.key_info.status}}
                            </div>
                        `;
                    }} else {{
                        statusDiv.innerHTML = `<div class="status error">❌ Invalid API Key: ${{data.message}}</div>`;
                    }}
                }} catch (error) {{
                    statusDiv.innerHTML = `<div class="status error">Error: ${{error.message}}</div>`;
                }}
            }}
            
            async function createKey() {{
                const keyName = document.getElementById('keyName').value.trim();
                const userEmail = document.getElementById('userEmail').value.trim();
                const organization = document.getElementById('organization').value.trim();
                const statusDiv = document.getElementById('createStatus');
                
                if (!keyName || !userEmail) {{
                    statusDiv.innerHTML = '<div class="status error">Please fill in all required fields</div>';
                    return;
                }}
                
                try {{
                    const response = await fetch('/admin/api/keys/', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{
                            name: keyName,
                            user_email: userEmail,
                            organization: organization || null,
                            daily_quota: 100,
                            rate_limit: 10
                        }})
                    }});
                    
                    const data = await response.json();
                    
                    if (response.ok) {{
                        statusDiv.innerHTML = `
                            <div class="status success">
                                ✅ API Key Created Successfully!<br>
                                <strong>API Key:</strong> <code>${{data.api_key}}</code><br>
                                <small>⚠️ Save this key now - it won't be shown again!</small>
                            </div>
                        `;
                        // Clear form
                        document.getElementById('keyName').value = '';
                        document.getElementById('userEmail').value = '';
                        document.getElementById('organization').value = '';
                    }} else {{
                        statusDiv.innerHTML = `<div class="status error">❌ Error: ${{data.detail}}</div>`;
                    }}
                }} catch (error) {{
                    statusDiv.innerHTML = `<div class="status error">Error: ${{error.message}}</div>`;
                }}
            }}
            
            async function loadKeys() {{
                const statusDiv = document.getElementById('keysList');
                statusDiv.innerHTML = '<div class="status">Loading keys...</div>';
                
                try {{
                    const response = await fetch('/admin/api/keys/');
                    const data = await response.json();
                    
                    if (response.ok) {{
                        let html = `<h4>Total Keys: ${{data.total_count}}</h4>`;
                        
                        if (data.api_keys.length === 0) {{
                            html += '<p>No API keys found.</p>';
                        }} else {{
                            html += '<table><tr><th>ID</th><th>Name</th><th>User</th><th>Organization</th><th>Status</th><th>Actions</th></tr>';
                            
                            data.api_keys.forEach(key => {{
                                html += `
                                    <tr>
                                        <td>${{key.id}}</td>
                                        <td>${{key.name}}</td>
                                        <td>${{key.user_email}}</td>
                                        <td>${{key.organization || 'None'}}</td>
                                        <td>${{key.status}}</td>
                                        <td>
                                            <button class="danger" onclick="revokeKey(${{key.id}})">Revoke</button>
                                        </td>
                                    </tr>
                                `;
                            }});
                            
                            html += '</table>';
                        }}
                        
                        statusDiv.innerHTML = html;
                    }} else {{
                        statusDiv.innerHTML = `<div class="status error">Error loading keys: ${{data.detail}}</div>`;
                    }}
                }} catch (error) {{
                    statusDiv.innerHTML = `<div class="status error">Error: ${{error.message}}</div>`;
                }}
            }}
            
            async function revokeKey(keyId) {{
                if (!confirm('Revoke this API key?')) return;
                
                try {{
                    const response = await fetch(`/admin/api/keys/${{keyId}}/revoke`, {{
                        method: 'POST'
                    }});
                    
                    if (response.ok) {{
                        alert('API key revoked!');
                        loadKeys();
                    }}
                }} catch (error) {{
                    alert(`Error: ${{error.message}}`);
                }}
            }}
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8004))
    uvicorn.run(app, host="0.0.0.0", port=port)
