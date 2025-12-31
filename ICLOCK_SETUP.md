# ZKTeco iClock/ADMS Protocol Setup

This guide explains how to use the **native ZKTeco iClock protocol** endpoints that receive **plain text (tab-separated)** data from your device.

## What's Different?

The iClock protocol is ZKTeco's native push protocol that:
- ✅ Uses **plain text** (tab-separated), not JSON
- ✅ Has two endpoints: heartbeat and data receiver
- ✅ Works with most ZKTeco devices (F-22, K-50, etc.)
- ✅ No API keys needed (uses device Serial Number)

## Endpoints Added

### 1. `/iclock/getrequest` (Heartbeat)
- **Method**: GET
- **Purpose**: Device pings this every 30-60 seconds to say "I'm alive"
- **Response**: Returns "OK"

### 2. `/iclock/cdata` (Data Receiver)
- **Method**: GET, POST
- **Purpose**: Receives attendance punch logs
- **Format**: Tab-separated plain text
- **Response**: Returns "OK"

## Quick Setup

### Step 1: Install Dependencies

```bash
cd zk-sync
source venv/Scripts/activate  # Windows Git Bash
# or
source venv/bin/activate       # Mac/Linux

pip install tabulate
```

### Step 2: Find Your Computer's IP Address

**Windows:**
```bash
ipconfig
# Look for "IPv4 Address" under your network adapter
# Example: 192.168.1.15
```

**Mac/Linux:**
```bash
ifconfig
# or
ip addr
# Look for inet address (usually 192.168.x.x)
```

### Step 3: Configure ZKTeco Device

1. **Access Device Menu**:
   - On device keypad: Menu → Comm. → Cloud Server Setting
   - Or via web interface: `http://device-ip` → Network → ADMS

2. **Set Server Address**:
   - **Server Address**: Your computer's IP (e.g., `192.168.1.15`)
   - **Server Port**: `5000`
   - **HTTPS**: **OFF** (for local testing)
   - **Protocol**: iClock (or ADMS)

3. **Save and Restart** device if required

### Step 4: Run Flask App

```bash
cd zk-sync
source venv/Scripts/activate
python app.py
```

You should see:
```
🚀 Flask running in DEVELOPMENT mode with auto-reload enabled
🌐 Server accessible at: http://0.0.0.0:5000
   ✅ Devices on your network can connect to this server
```

### Step 5: Test Connection

1. **Wait for Heartbeat** (within 1 minute):
   ```
   💓 [2025-12-30 15:30:45] HEARTBEAT from Device
      📱 Serial Number: ABC123456
      📍 Device IP: 192.168.1.100
      ✅ Device is alive and connected
   ```

2. **Make a Test Punch**:
   - Scan your fingerprint or card on the device
   - You should immediately see in console:

   ```
   ================================================================================
   📥 [2025-12-30 15:31:20] NEW PUSH DATA RECEIVED (iClock Protocol)
   ================================================================================
   📱 Serial Number: ABC123456
   📋 Table: ATTLOG
   📍 Device IP: 192.168.1.100
   🌐 Method: POST
   
   📦 RAW DATA RECEIVED:
   --------------------------------------------------------------------------------
   123	2025-12-30 15:31:20	0	15	0
   --------------------------------------------------------------------------------
   
   🔍 Parsing attendance data...
      Found 1 line(s)
      ✅ Line 1: User 123 - Check In at 2025-12-30 15:31:20
   
   📊 PARSED ATTENDANCE DATA:
   +----------+---------------------+----------+--------+------------+
   | User ID  | Timestamp           | Status   | Verify | Work Code  |
   +==========+=====================+==========+========+============+
   | 123      | 2025-12-30 15:31:20 | Check In | 15     | 0          |
   +----------+---------------------+----------+--------+------------+
   ```

## Data Format

The device sends data in **tab-separated** format:

```
USERID \t TIMESTAMP \t STATUS \t VERIFY \t WORKCODE
```

**Example:**
```
123	2025-12-30 15:31:20	0	15	0
```

**Field Meanings:**
- **USERID**: Employee ID (e.g., "123")
- **TIMESTAMP**: Date and time (format: `YYYY-MM-DD HH:MM:SS`)
- **STATUS**: `0` = Check In, `1` = Check Out
- **VERIFY**: Verification method (15 = Fingerprint, 1 = Password, etc.)
- **WORKCODE**: Work code (usually 0)

## Automatic Backend Upload

If you have `DEV_BACKEND_URL` or `PROD_BACKEND_URL` configured in `.env`, the system will automatically:

1. Parse the attendance data
2. Format it for your HRMS backend
3. Upload it using the `/attendance/upload` endpoint
4. Use `ADMS_SERVICE_TOKEN` for authentication (if configured)

**Example output:**
```
📤 Forwarding to backend...
   Environment: DEV
   Backend URL: https://code-huddle-hrms-dev-61ae656862e5.herokuapp.com
   ✅ Successfully uploaded to backend!
   Status Code: 200
```

## Troubleshooting

### Problem: No heartbeat received

**Solutions:**
1. Check device and computer are on same network
2. Verify device Server Address is correct (your computer's IP)
3. Check Windows Firewall allows port 5000
4. Try disabling firewall temporarily to test

**Windows Firewall:**
```bash
# Allow port 5000
netsh advfirewall firewall add rule name="Flask iClock" dir=in action=allow protocol=TCP localport=5000
```

### Problem: Heartbeat works but no data received

**Solutions:**
1. Make sure device is configured to push data (not just heartbeat)
2. Check device settings for "Real-time Upload" or "Push Mode"
3. Verify device has attendance records to send
4. Check device logs/status

### Problem: Data received but not parsed correctly

**Solutions:**
1. Check the "RAW DATA RECEIVED" section in console
2. Verify format matches: `USERID \t TIMESTAMP \t STATUS \t VERIFY \t WORKCODE`
3. Some devices may use different separators or formats
4. Check device firmware version

### Problem: Backend upload fails

**Solutions:**
1. Verify `DEV_BACKEND_URL` or `PROD_BACKEND_URL` is set in `.env`
2. Check `ADMS_SERVICE_TOKEN` is valid (get from HRMS login)
3. Verify backend endpoint `/attendance/upload` exists
4. Check backend logs for error details

## Configuration Options

Add to `.env`:

```env
# Flask host (0.0.0.0 = accessible from network, 127.0.0.1 = localhost only)
FLASK_HOST=0.0.0.0

# Flask port
FLASK_PORT=5000

# Backend URLs for auto-upload
DEV_BACKEND_URL=https://your-dev-backend.com
PROD_BACKEND_URL=https://your-prod-backend.com

# Service token for backend authentication
ADMS_SERVICE_TOKEN=your-token-here

# Default environment
ADMS_DEFAULT_ENV=dev
```

## Comparison: iClock vs JSON Webhook

| Feature | iClock Protocol | JSON Webhook |
|---------|----------------|--------------|
| **Format** | Plain text (tab-separated) | JSON |
| **Endpoints** | `/iclock/getrequest`, `/iclock/cdata` | `/adms/webhook` |
| **Heartbeat** | Yes (every 30-60s) | No |
| **Device Support** | Most ZKTeco devices | F-22, newer models |
| **Authentication** | Serial Number (SN) | API Key (optional) |
| **Setup** | Device native protocol | Custom webhook URL |

## Next Steps

1. ✅ Test heartbeat connection
2. ✅ Make test punches and verify data appears
3. ✅ Configure backend URL for auto-upload
4. ✅ Set up service token for authentication
5. ✅ Monitor logs for any issues

## Production Deployment

For production:
1. Deploy to a server with public IP/domain
2. Use HTTPS (configure reverse proxy)
3. Update device Server Address to your public URL
4. Consider adding IP whitelisting for security
5. Set up proper logging and monitoring

---

**Note**: The iClock protocol endpoints work alongside the existing `/adms/webhook` JSON endpoint. You can use either or both depending on your device capabilities.

