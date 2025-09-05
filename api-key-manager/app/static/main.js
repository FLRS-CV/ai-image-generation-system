// Global variables
let currentUserRole = null;
let currentApiKey = null;
let validationTimeout = null;

// Tab Management
function showTab(tabName) {
    // Hide all tab contents
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(content => {
        content.classList.remove('active');
    });

    // Remove active class from all tabs
    const tabs = document.querySelectorAll('.nav-tab');
    tabs.forEach(tab => {
        tab.classList.remove('active');
    });

    // Show selected tab
    const selectedTab = document.getElementById(tabName);
    const selectedButton = document.getElementById(`tab-${tabName}`);
    
    if (selectedTab) selectedTab.classList.add('active');
    if (selectedButton) selectedButton.classList.add('active');
}

function showAdminTab(tabName) {
    // Hide all admin tab contents
    const adminTabContents = document.querySelectorAll('#admin .tab-content');
    adminTabContents.forEach(content => {
        content.classList.remove('active');
    });

    // Remove active class from all admin tabs
    const adminTabs = document.querySelectorAll('#admin .nav-tab');
    adminTabs.forEach(tab => {
        tab.classList.remove('active');
    });

    // Show selected admin tab
    const selectedTab = document.getElementById(`admin-${tabName}`);
    const selectedButton = document.getElementById(`admin-tab-${tabName}`);
    
    if (selectedTab) selectedTab.classList.add('active');
    if (selectedButton) selectedButton.classList.add('active');
}

// API Key Validation
async function validateAPIKey() {
    const apiKeyInput = document.getElementById('apiKey');
    const apiKey = apiKeyInput.value.trim();
    const statusDiv = document.getElementById('apiKeyStatus');

    // Clear previous timeout
    if (validationTimeout) {
        clearTimeout(validationTimeout);
    }

    if (!apiKey) {
        statusDiv.innerHTML = '';
        statusDiv.className = 'api-key-status';
        apiKeyInput.className = 'api-key-input';
        hideMainContent();
        return;
    }

    // Show validating status
    statusDiv.innerHTML = '🔍 Validating API key...';
    statusDiv.className = 'api-key-status validating';
    apiKeyInput.className = 'api-key-input';

    // Debounce validation requests
    validationTimeout = setTimeout(async () => {
        try {
            const response = await fetch('/api/keys/validate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ api_key: apiKey })
            });

            console.log('Response status:', response.status);
            const result = await response.json();
            console.log('Response data:', result);

            if (result.valid) {
                const role = result.key_info ? result.key_info.role : 'user';
                statusDiv.innerHTML = `✅ Valid API key! Role: <span class="role-badge ${role}">${role.toUpperCase()}</span>`;
                statusDiv.className = 'api-key-status valid';
                apiKeyInput.className = 'api-key-input valid';
                
                // Store user info and show content
                currentUserRole = role;
                currentApiKey = apiKey;
                showMainContent({role: role, ...result.key_info});
            } else {
                statusDiv.innerHTML = '❌ Invalid API key. Please check and try again.';
                statusDiv.className = 'api-key-status invalid';
                apiKeyInput.className = 'api-key-input invalid';
                hideMainContent();
            }
        } catch (error) {
            console.error('Error validating API key:', error);
            console.error('Error stack:', error.stack);
            statusDiv.innerHTML = `⚠️ Error validating API key: ${error.message}. Check console for details.`;
            statusDiv.className = 'api-key-status invalid';
            apiKeyInput.className = 'api-key-input invalid';
            hideMainContent();
        }
    }, 800); // Wait 800ms after user stops typing
}

function showMainContent(userInfo) {
    const mainContent = document.getElementById('mainContent');
    const authSection = document.getElementById('authSection');
    const userInfoSpan = document.getElementById('userInfo');
    
    // Update user info display
    userInfoSpan.innerHTML = ` - Logged in as <span class="role-badge ${userInfo.role}">${userInfo.role.toUpperCase()}</span>`;
    userInfoSpan.classList.remove('hidden');

    // Show main content
    mainContent.classList.remove('hidden');
    authSection.style.display = 'none';

    // Configure role-based UI
    configureRoleBasedUI(userInfo.role);
}

function hideMainContent() {
    const mainContent = document.getElementById('mainContent');
    const authSection = document.getElementById('authSection');
    const userInfoSpan = document.getElementById('userInfo');
    
    mainContent.classList.add('hidden');
    authSection.style.display = 'block';
    userInfoSpan.classList.add('hidden');
    currentUserRole = null;
    currentApiKey = null;
}

function configureRoleBasedUI(role) {
    const adminTab = document.getElementById('tab-admin');
    const roleSelection = document.getElementById('roleSelection');
    const manageTab = document.getElementById('admin-tab-manage');

    // Reset visibility
    adminTab.classList.add('hidden');
    roleSelection.classList.add('hidden');
    manageTab.classList.add('hidden');

    if (role === 'superadmin') {
        // Super admin sees everything
        adminTab.classList.remove('hidden');
        roleSelection.classList.remove('hidden');
        manageTab.classList.remove('hidden');
    } else if (role === 'admin') {
        // Admin sees admin tab but not role selection or key management
        adminTab.classList.remove('hidden');
    }
    // Users only see virtual staging tab (which is always visible)
}

// Virtual Staging Functions
function previewImage() {
    const fileInput = document.getElementById('imageFile');
    const preview = document.getElementById('imagePreview');

    if (fileInput.files && fileInput.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            preview.src = e.target.result;
            preview.style.display = 'block';
        };
        reader.readAsDataURL(fileInput.files[0]);
    }
}

async function generateVirtualStaging() {
    const fileInput = document.getElementById('imageFile');
    const numImages = document.getElementById('numImages').value;
    const style = document.getElementById('style').value;
    const loadingDiv = document.getElementById('loading');
    const resultsDiv = document.getElementById('stagingResults');

    if (!fileInput.files || !fileInput.files[0]) {
        showStatus(resultsDiv, 'Please select an image file first.', 'error');
        return;
    }

    if (!currentApiKey) {
        showStatus(resultsDiv, 'Please authenticate with a valid API key first.', 'error');
        return;
    }

    // Show loading
    loadingDiv.style.display = 'block';
    resultsDiv.innerHTML = '';

    try {
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('num_images', numImages);
        formData.append('style', style);

        const response = await fetch('/api/virtual-staging/generate', {
            method: 'POST',
            headers: {
                'X-API-Key': currentApiKey
            },
            body: formData
        });

        const result = await response.json();

        if (response.ok) {
            displayStagingResults(result);
        } else {
            showStatus(resultsDiv, `Error: ${result.detail || 'Failed to generate virtual staging'}`, 'error');
        }
    } catch (error) {
        console.error('Error generating virtual staging:', error);
        showStatus(resultsDiv, 'Network error. Please try again.', 'error');
    } finally {
        loadingDiv.style.display = 'none';
    }
}

function displayStagingResults(result) {
    const resultsDiv = document.getElementById('stagingResults');
    
    if (result.images && result.images.length > 0) {
        let html = `
            <div class="status success">
                ✅ Successfully generated ${result.images.length} virtual staging image(s)!
            </div>
            <div class="result-gallery">
        `;

        result.images.forEach((imagePath, index) => {
            html += `
                <div class="result-item">
                    <img src="/${imagePath}" alt="Virtual Staging ${index + 1}" class="result-image" />
                    <h4>Variation ${index + 1}</h4>
                    <a href="/${imagePath}" download="virtual_staging_${index + 1}.png">
                        <button>📥 Download</button>
                    </a>
                </div>
            `;
        });

        html += '</div>';
        resultsDiv.innerHTML = html;
    } else {
        showStatus(resultsDiv, 'No images were generated. Please try again.', 'warning');
    }
}

// Admin Functions
async function validateKey() {
    const keyToValidate = document.getElementById('validateKey').value.trim();
    const statusDiv = document.getElementById('validateStatus');

    if (!keyToValidate) {
        showStatus(statusDiv, 'Please enter an API key to validate.', 'error');
        return;
    }

    try {
        const response = await fetch('/api/keys/validate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': currentApiKey
            },
            body: JSON.stringify({ api_key: keyToValidate })
        });

        const result = await response.json();

        if (result.valid) {
            const role = result.key_info ? result.key_info.role : 'user';
            const usageCount = result.key_info ? result.key_info.current_daily_usage : 0;
            const dailyQuota = result.key_info ? result.key_info.daily_quota : 'Unlimited';
            const rateLimit = result.key_info ? result.key_info.rate_limit : 60;
            
            showStatus(statusDiv, 
                `✅ Valid API key! Role: <span class="role-badge ${role}">${role.toUpperCase()}</span><br>
                📊 Usage: ${usageCount} requests<br>
                📈 Daily Quota: ${dailyQuota}<br>
                ⚡ Rate Limit: ${rateLimit} req/min`, 
                'success'
            );
        } else {
            showStatus(statusDiv, '❌ Invalid API key.', 'error');
        }
    } catch (error) {
        console.error('Error validating key:', error);
        showStatus(statusDiv, 'Error validating key. Please try again.', 'error');
    }
}

async function createKey() {
    const keyName = document.getElementById('keyName').value.trim();
    const userEmail = document.getElementById('userEmail').value.trim();
    const organization = document.getElementById('organization').value.trim();
    const dailyQuota = document.getElementById('dailyQuota').value;
    const rateLimit = document.getElementById('rateLimit').value;
    const userRole = document.getElementById('userRole').value;
    const statusDiv = document.getElementById('createStatus');

    if (!keyName || !userEmail) {
        showStatus(statusDiv, 'Please fill in the required fields (Key Name and User Email).', 'error');
        return;
    }

    const requestData = {
        name: keyName,
        user_email: userEmail,
        daily_quota: parseInt(dailyQuota),
        rate_limit: parseInt(rateLimit)
    };

    if (organization) {
        requestData.organization = organization;
    }

    // Only include role if user is super admin
    if (currentUserRole === 'superadmin') {
        requestData.role = userRole;
    }

    try {
        const response = await fetch('/api/keys/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': currentApiKey
            },
            body: JSON.stringify(requestData)
        });

        const result = await response.json();

        if (response.ok) {
            const role = result.key_info ? result.key_info.role : 'user';
            const userEmail = result.key_info ? result.key_info.user_email : 'Unknown';
            
            showStatus(statusDiv, 
                `✅ API key created successfully!<br>
                🔑 <strong>API Key:</strong> <code style="background:#f0f0f0;padding:2px 6px;border-radius:3px;">${result.api_key}</code><br>
                📧 <strong>User:</strong> ${userEmail}<br>
                👤 <strong>Role:</strong> <span class="role-badge ${role}">${role.toUpperCase()}</span><br>
                <em>⚠️ Save this key securely - it won't be shown again!</em>`, 
                'success'
            );

            // Clear form
            document.getElementById('keyName').value = '';
            document.getElementById('userEmail').value = '';
            document.getElementById('organization').value = '';
            document.getElementById('dailyQuota').value = '100';
            document.getElementById('rateLimit').value = '60';
            document.getElementById('userRole').value = 'user';
        } else {
            showStatus(statusDiv, `❌ Error creating key: ${result.detail || 'Unknown error'}`, 'error');
        }
    } catch (error) {
        console.error('Error creating key:', error);
        showStatus(statusDiv, 'Network error. Please try again.', 'error');
    }
}

async function loadKeys() {
    if (currentUserRole !== 'superadmin') {
        showStatus(document.getElementById('keysList'), 'Access denied. Only super admins can view all keys.', 'error');
        return;
    }

    const keysListDiv = document.getElementById('keysList');
    
    try {
        showStatus(keysListDiv, '🔄 Loading API keys...', 'info');

        const response = await fetch('/api/keys/', {
            headers: {
                'X-API-Key': currentApiKey
            }
        });

        const result = await response.json();

        if (response.ok && result.api_keys) {
            displayKeysList(result.api_keys);
        } else {
            showStatus(keysListDiv, `❌ Error loading keys: ${result.detail || 'Unknown error'}`, 'error');
        }
    } catch (error) {
        console.error('Error loading keys:', error);
        showStatus(keysListDiv, 'Network error. Please try again.', 'error');
    }
}

function displayKeysList(keys) {
    const keysListDiv = document.getElementById('keysList');
    
    if (keys.length === 0) {
        showStatus(keysListDiv, '📝 No API keys found.', 'info');
        return;
    }

    let html = `
        <div style="margin-top: 20px;">
            <h4>📋 API Keys (${keys.length} total)</h4>
            <div style="overflow-x: auto;">
                <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
                    <thead>
                        <tr style="background-color: #f8f9fa;">
                            <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Name</th>
                            <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">User</th>
                            <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Role</th>
                            <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Usage</th>
                            <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Status</th>
                            <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Created</th>
                            <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
    `;

    keys.forEach(key => {
        const isActive = key.is_active === undefined ? true : key.is_active;
        const statusBadge = isActive ? 
            '<span style="background: #28a745; color: white; padding: 2px 6px; border-radius: 10px; font-size: 11px;">ACTIVE</span>' :
            '<span style="background: #dc3545; color: white; padding: 2px 6px; border-radius: 10px; font-size: 11px;">REVOKED</span>';

        html += `
            <tr>
                <td style="border: 1px solid #ddd; padding: 8px;">${key.name || 'Unnamed'}</td>
                <td style="border: 1px solid #ddd; padding: 8px;">${key.user_email || 'Unknown'}</td>
                <td style="border: 1px solid #ddd; padding: 8px;">
                    <span class="role-badge ${key.role || 'user'}">${(key.role || 'user').toUpperCase()}</span>
                </td>
                <td style="border: 1px solid #ddd; padding: 8px;">${key.usage_count || 0}/${key.daily_quota || '∞'}</td>
                <td style="border: 1px solid #ddd; padding: 8px;">${statusBadge}</td>
                <td style="border: 1px solid #ddd; padding: 8px;">${new Date(key.created_at).toLocaleDateString()}</td>
                <td style="border: 1px solid #ddd; padding: 8px;">
                    ${isActive ? 
                        `<button onclick="revokeKey(${key.id})" class="danger" style="padding: 4px 8px; font-size: 12px;">🚫 Revoke</button>` :
                        '<span style="color: #999;">Revoked</span>'
                    }
                </td>
            </tr>
        `;
    });

    html += `
                    </tbody>
                </table>
            </div>
        </div>
    `;

    keysListDiv.innerHTML = html;
}

async function revokeKey(keyId) {
    if (!confirm('Are you sure you want to revoke this API key? This action cannot be undone.')) {
        return;
    }

    try {
        const response = await fetch(`/api/keys/${keyId}/revoke`, {
            method: 'POST',
            headers: {
                'X-API-Key': currentApiKey
            }
        });

        const result = await response.json();

        if (response.ok) {
            showStatus(document.getElementById('keysList'), '✅ API key revoked successfully!', 'success');
            // Reload the keys list
            setTimeout(() => loadKeys(), 1000);
        } else {
            showStatus(document.getElementById('keysList'), `❌ Error revoking key: ${result.detail || 'Unknown error'}`, 'error');
        }
    } catch (error) {
        console.error('Error revoking key:', error);
        showStatus(document.getElementById('keysList'), 'Network error. Please try again.', 'error');
    }
}

function refreshKeys() {
    loadKeys();
}

// Utility Functions
function showStatus(element, message, type) {
    element.innerHTML = `<div class="status ${type}">${message}</div>`;
}

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    // Focus on API key input
    document.getElementById('apiKey').focus();
    
    // Set up initial state
    hideMainContent();
});
