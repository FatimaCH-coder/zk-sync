# How to Get ADMS Configuration Values

This guide explains where to get each value for your `.env` file.

## 1. ADMS_API_KEY

**What it is:** A secure random string used to authenticate requests from your ZKTeco device.

**How to generate it:**

### Option A: Using Python (Recommended)
```bash
cd zk-sync
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Option B: Using the helper script
```bash
cd zk-sync
python generate_env_keys.py
```

### Option C: Online Generator
Visit: https://randomkeygen.com/ and use a "Fort Knox Password" or "CodeIgniter Encryption Keys"

**Example:**
```
ADMS_API_KEY=6FmE_9P_LiK2wjqzjOjMziSQa-L0Q4dKoEsQOAccdQA
```

**Important:** 
- Keep this secret and secure
- Use the same key in your ZKTeco device configuration
- Don't commit it to git (it's already in .gitignore)

---

## 2. ADMS_DEFAULT_ENV

**What it is:** The default environment for ADMS uploads (dev or prod).

**How to set it:**
- Just choose `dev` or `prod` based on your needs
- `dev` = Development/Testing environment
- `prod` = Production environment

**Example:**
```env
ADMS_DEFAULT_ENV=dev
```

or

```env
ADMS_DEFAULT_ENV=prod
```

---

## 3. ADMS_SERVICE_TOKEN

**What it is:** An authentication token from your HRMS backend to allow ADMS webhook to upload attendance data.

**How to get it:**

### Method 1: From Backend Login (Easiest)

1. **Login to your HRMS system** using the web interface
2. **Open Browser DevTools** (Press F12)
3. **Go to Network tab**
4. **Look for the login request** (usually `/auth/login` or similar)
5. **Click on the request** and go to "Response" tab
6. **Find the token** - look for:
   - `access_token`
   - `accessToken`
   - `tokens.access_token`
   - `tokens.accessToken`
7. **Copy the token value**

**Example response:**
```json
{
  "tokens": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "..."
  }
}
```

Copy the `access_token` value.

### Method 2: Using Your App's Login

1. **Run your zk-sync app**
2. **Login through the web interface**
3. **Open Browser DevTools** (F12)
4. **Go to Application/Storage tab**
5. **Check Local Storage or Session Storage**
6. **Look for `accessToken` or `access_token`**
7. **Copy the value**

### Method 3: From Backend API Directly

If you have API access to your backend:

```bash
curl -X POST https://your-backend.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-email@example.com",
    "password": "your-password",
    "role": "admin"
  }'
```

Extract the `access_token` from the response.

### Method 4: Service Account Token

If your backend supports service accounts:
1. Contact your backend administrator
2. Request a service account token for ADMS
3. This is preferred for production as it doesn't expire like user tokens

### Method 5: Leave Empty (If Backend Doesn't Require Auth)

If your backend's `/attendance/upload` endpoint doesn't require authentication, you can leave it empty:

```env
ADMS_SERVICE_TOKEN=
```

**Example:**
```env
ADMS_SERVICE_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

**Important:**
- Tokens usually expire after some time (e.g., 24 hours, 7 days)
- You may need to update this periodically
- For production, use a service account token that doesn't expire
- Keep this secret and secure

---

## Complete .env Example

```env
# Backend URLs
DEV_BACKEND_URL=https://code-huddle-hrms-dev-61ae656862e5.herokuapp.com
PROD_BACKEND_URL=http://localhost:3001

# ADMS Configuration
ADMS_API_KEY=6FmE_9P_LiK2wjqzjOjMziSQa-L0Q4dKoEsQOAccdQA
ADMS_DEFAULT_ENV=dev
ADMS_SERVICE_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Other settings
SECRET_KEY=your-secret-key-here
FLASK_DEBUG=True
```

---

## Quick Setup Commands

```bash
# 1. Generate API key
cd zk-sync
python -c "import secrets; print('ADMS_API_KEY=' + secrets.token_urlsafe(32))" >> .env

# 2. Add default environment
echo "ADMS_DEFAULT_ENV=dev" >> .env

# 3. Add service token (you need to get this manually)
echo "ADMS_SERVICE_TOKEN=your-token-here" >> .env
```

---

## Testing Your Configuration

After setting up, test the ADMS endpoint:

```bash
# Check if endpoint is active
curl http://localhost:5000/adms/status

# Test webhook (replace API_KEY with your generated key)
curl -X POST http://localhost:5000/adms/webhook \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{
    "user_id": "123",
    "timestamp": "2025-12-30T10:30:00",
    "punch": 0,
    "name": "Test User"
  }'
```

---

## Troubleshooting

**Problem:** "Invalid API key" error
- **Solution:** Make sure `ADMS_API_KEY` in `.env` matches what you configured in your ZKTeco device

**Problem:** "Upload failed" - 401 Unauthorized
- **Solution:** Your `ADMS_SERVICE_TOKEN` is expired or invalid. Get a new token from login.

**Problem:** "Upload failed" - 403 Forbidden
- **Solution:** The token doesn't have permission. Use an admin account token or service account.

**Problem:** Token expires frequently
- **Solution:** Use a service account token or implement token refresh logic (future enhancement).

