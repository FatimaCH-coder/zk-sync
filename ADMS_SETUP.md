# ADMS (Push SDK) Setup Guide

This guide explains how to configure the Push SDK (ADMS) method for real-time attendance data from ZKTeco devices.

## What is ADMS?

ADMS (Attendance Management Data Service) is ZKTeco's Push SDK that allows devices to automatically send attendance records to your server in real-time. This is superior to the Pull SDK method because:

- ✅ Works across different networks (no port forwarding needed)
- ✅ Real-time data (instant push when employee punches in/out)
- ✅ Lower server load (only processes data when events occur)
- ✅ Better scalability (devices initiate connections)

## Prerequisites

1. ZKTeco device with ADMS support (F-22, K-50 with ADMS, or compatible models)
2. Server with public IP/domain (for device to connect to)
3. Flask application deployed and accessible

## Step-by-Step Setup

### 1. Deploy Your Application

Deploy this Flask application to a server accessible from the internet:

```bash
# Example: Deploy to a cloud server
# Make sure port 5000 (or your chosen port) is open
# For production, use HTTPS with a reverse proxy (nginx, Apache)
```

**Important:** Your server must be accessible via a public URL. Examples:
- `https://attendance.yourcompany.com`
- `http://your-server-ip:5000` (less secure, not recommended for production)

### 2. Configure Environment Variables

Add these to your `.env` file:

```env
# ADMS Configuration
ADMS_API_KEY=your-secure-random-api-key-12345  # Generate a secure random string
ADMS_DEFAULT_ENV=dev  # or 'prod'
ADMS_SERVICE_TOKEN=your-backend-service-token  # Optional: for backend auth
```

**Generate a secure API key:**
```python
import secrets
print(secrets.token_urlsafe(32))
```

### 3. Configure ZKTeco Device

#### For ZKTeco F-22 (Web Interface):

1. Connect to device's web interface: `http://device-ip`
2. Login with admin credentials
3. Navigate to: **Network** → **ADMS Settings**
4. Enable ADMS
5. Set **Server URL**: `http://your-server.com:5000/adms/webhook`
   - For HTTPS: `https://your-server.com/adms/webhook`
   - If using API key: `http://your-server.com:5000/adms/webhook?api_key=your-api-key`
6. Set **Port**: Usually 80 (HTTP) or 443 (HTTPS)
7. Save and restart device if required

#### For ZKTeco K-50 or Other Models:

1. Access device menu (usually via device keypad or software)
2. Navigate to: **Network Settings** → **ADMS** or **Push Settings**
3. Enable ADMS/Push function
4. Enter server URL: `http://your-server.com:5000/adms/webhook`
5. Save configuration

### 4. Test the Connection

#### Test 1: Check Endpoint Status

Visit in browser: `http://your-server.com:5000/adms/status`

Expected response:
```json
{
  "status": "active",
  "endpoint": "/adms/webhook",
  "methods": ["POST", "GET"],
  "api_key_required": true,
  "default_environment": "dev"
}
```

#### Test 2: Manual Webhook Test

You can test the webhook manually using curl:

```bash
curl -X POST http://your-server.com:5000/adms/webhook \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "user_id": "123",
    "timestamp": "2025-12-30T10:30:00",
    "punch": 0,
    "name": "Test User"
  }'
```

#### Test 3: Real Device Test

1. Make a test punch on the ZKTeco device
2. Check server logs for incoming request
3. Verify data appears in your HRMS backend

### 5. Monitor and Debug

#### Check Server Logs

The application logs all ADMS webhook requests:

```bash
# Look for messages like:
ADMS: Successfully processed attendance from device 192.168.1.100 - User: John Doe, Time: 2025-12-30T10:30:00
```

#### Common Issues

**Issue:** Device not sending data
- **Solution:** Check device network settings, ensure ADMS is enabled, verify server URL is correct

**Issue:** 401 Unauthorized error
- **Solution:** Verify API key matches in both `.env` and device configuration

**Issue:** Data not appearing in backend
- **Solution:** Check `ADMS_SERVICE_TOKEN` is set correctly, verify backend URL is accessible

**Issue:** Connection timeout
- **Solution:** Ensure server firewall allows incoming connections on port 5000, check device can reach server

## Data Format

The ADMS endpoint accepts multiple data formats. Common formats:

### Format 1: Direct JSON
```json
{
  "user_id": "123",
  "timestamp": "2025-12-30T10:30:00",
  "punch": 0,
  "name": "John Doe"
}
```

### Format 2: Nested Structure
```json
{
  "data": {
    "userId": "123",
    "time": "2025-12-30 10:30:00",
    "status": 0,
    "name": "John Doe"
  }
}
```

### Format 3: Query Parameters (GET)
```
GET /adms/webhook?user_id=123&timestamp=2025-12-30T10:30:00&punch=0&name=John+Doe&api_key=your-key
```

## Security Considerations

1. **Use HTTPS in Production:** Always use HTTPS for production deployments
2. **API Key Authentication:** Always set `ADMS_API_KEY` for production
3. **Firewall Rules:** Restrict access to ADMS endpoint if possible
4. **Rate Limiting:** Consider adding rate limiting for production
5. **IP Whitelisting:** Optionally whitelist device IPs (if static)

## Production Deployment

For production, consider:

1. **Reverse Proxy (nginx/Apache):**
   ```nginx
   location /adms/webhook {
       proxy_pass http://localhost:5000;
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
       proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
   }
   ```

2. **HTTPS Certificate:** Use Let's Encrypt or commercial SSL certificate

3. **Process Manager:** Use systemd, supervisor, or PM2 to keep app running

4. **Logging:** Set up proper logging and monitoring

## Comparison: ADMS vs Pull SDK

| Aspect | Pull SDK | ADMS (Push SDK) |
|--------|----------|-----------------|
| **Network** | Requires port forwarding | Works across any network |
| **Real-Time** | No (polling) | Yes (instant) |
| **Server Load** | High | Low |
| **Setup Complexity** | Medium | Low |
| **Best For** | Single location | Multiple locations |

## Support

For issues or questions:
1. Check server logs for error messages
2. Verify device ADMS configuration
3. Test endpoint manually with curl
4. Check network connectivity between device and server

