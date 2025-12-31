# Complete .env File Example

Here's a complete example of your `.env` file with all required variables:

```env
# ============================================
# Device Configuration (Pull SDK Method)
# ============================================
# Device IPs for dropdown in the web interface
# Format: IP:PORT or just IP (default port is 4370)
DEVICE_IP_1=192.168.1.100:4370
DEVICE_IP_2=192.168.1.101:4370

# ============================================
# Backend URLs
# ============================================
# Development backend URL (your dev/staging HRMS API)
# Replace with your actual dev backend URL
DEV_BACKEND_URL=https://code-huddle-hrms-dev-61ae656862e5.herokuapp.com

# Production backend URL (your production HRMS API)
# Replace with your actual production backend URL
PROD_BACKEND_URL=https://your-production-api.com

# ============================================
# HRMS Frontend URLs (Optional - for redirect links)
# ============================================
# Development HRMS web interface URL
DEV_HRMS_URL=https://dev-hrms.yourcompany.com

# Production HRMS web interface URL
PROD_HRMS_URL=https://hrms.yourcompany.com

# ============================================
# Flask Configuration
# ============================================
# Secret key for Flask sessions
# Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=VIrDuiMZBEoBrXwCVMrwW5L_Or6pmTTcf1M780zO9Pg

# Enable Flask debug mode with auto-reload (True/False)
FLASK_DEBUG=True

# Flask port (optional, defaults to 5000)
# FLASK_PORT=5000

# Flask host (optional, defaults to 0.0.0.0)
# 0.0.0.0 = accessible from network, 127.0.0.1 = localhost only
# FLASK_HOST=0.0.0.0

# ============================================
# ngrok Configuration (for Network Switching)
# ============================================
# Enable ngrok tunnel for public URL (works from any network)
# Set to True to automatically create a public URL when Flask starts
ENABLE_NGROK=False

# ngrok authentication token (optional but recommended)
# Get from https://ngrok.com (sign up for free account)
# NGROK_AUTH_TOKEN=your-ngrok-auth-token-here

# ============================================
# ADMS (Push SDK) Configuration
# ============================================
# API Key for ADMS webhook authentication
# Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
ADMS_API_KEY=teyChB30Kjeoo0zi8NAGlHgaEtubCBQKU-s3rlPexaM

# Default environment for ADMS uploads (dev or prod)
ADMS_DEFAULT_ENV=dev

# Service token for backend authentication
# Get this from your HRMS login (see GET_ENV_VALUES.md)
ADMS_SERVICE_TOKEN=your-backend-access-token-here
```

## What You Need to Fill In:

### ✅ Already Have (Keep These):
- `DEVICE_IP_1` and `DEVICE_IP_2` - Your device IPs
- `FLASK_DEBUG=True` - Keep this for development

### 🔧 Need to Fill In:

1. **DEV_BACKEND_URL** - Your development backend API URL
   - Example: `https://code-huddle-hrms-dev-61ae656862e5.herokuapp.com`
   - This is where attendance data gets uploaded

2. **PROD_BACKEND_URL** - Your production backend API URL
   - Example: `https://api.yourcompany.com`
   - Leave as placeholder if you don't have production yet

3. **DEV_HRMS_URL** - Your development HRMS web interface
   - Example: `https://dev-hrms.yourcompany.com`
   - Used for redirect links in the UI

4. **PROD_HRMS_URL** - Your production HRMS web interface
   - Example: `https://hrms.yourcompany.com`
   - Used for redirect links in the UI

5. **SECRET_KEY** - Generate a new one:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

6. **ADMS_API_KEY** - Generate a new one:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

7. **ADMS_SERVICE_TOKEN** - Get from your HRMS login:
   - Login to HRMS → Open DevTools (F12) → Network tab → Find login request → Copy `access_token`
   - See `GET_ENV_VALUES.md` for detailed instructions

## Quick Setup Commands:

```bash
cd zk-sync

# Generate SECRET_KEY
echo "SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")" >> .env

# Generate ADMS_API_KEY
echo "ADMS_API_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")" >> .env

# Add ADMS configuration
echo "ADMS_DEFAULT_ENV=dev" >> .env
echo "ADMS_SERVICE_TOKEN=" >> .env  # Fill this manually after getting token
```

## Your Current .env Should Look Like:

```env
# Device IPs
DEVICE_IP_1=192.111.11.111:4370
DEVICE_IP_2=192.222.22.222:4370

# Backend URLs (FILL THESE IN)
DEV_BACKEND_URL=https://your-dev-backend-url.com
PROD_BACKEND_URL=https://your-prod-backend-url.com

# HRMS URLs (FILL THESE IN - Optional)
DEV_HRMS_URL=https://dev-hrms.yourcompany.com
PROD_HRMS_URL=https://hrms.yourcompany.com

# Flask
SECRET_KEY=VIrDuiMZBEoBrXwCVMrwW5L_Or6pmTTcf1M780zO9Pg
FLASK_DEBUG=True

# ADMS Configuration (ADD THESE)
ADMS_API_KEY=teyChB30Kjeoo0zi8NAGlHgaEtubCBQKU-s3rlPexaM
ADMS_DEFAULT_ENV=dev
ADMS_SERVICE_TOKEN=your-token-from-hrms-login

# ngrok Configuration (for Network Switching)
# Set ENABLE_NGROK=True to create a public URL that works from any network
# See NETWORK_SETUP.md for details
ENABLE_NGROK=False
# NGROK_AUTH_TOKEN=your-ngrok-token-here
```

## Notes:

- **Backend URLs**: These should point to your HRMS API endpoints (the backend that receives attendance data)
- **HRMS URLs**: These are optional - they're just for redirect links in the UI
- **ADMS_SERVICE_TOKEN**: This is optional if your backend doesn't require authentication, but recommended for security
- All generated keys are examples - generate your own for security!

