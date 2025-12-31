# How the "Connect" Button Works

This document explains how your current connection system works using the **Pull SDK** method.

## Overview

The "Connect" button uses the **Pull SDK** method, which means:
- **Your server** (Flask app) **initiates** the connection to the ZKTeco device
- You **manually** connect when you click the button
- The connection is **temporary** - it connects, gets data, then disconnects
- Requires the device to be on the **same network** (or accessible via port forwarding)

---

## Step-by-Step Flow

### 1. User Clicks "Connect" Button

```
[Browser] → User clicks "Connect" button
```

**Frontend Code** (`index.html`):
```javascript
async function connectDevice() {
  selectedDevice = document.getElementById("deviceSelect").value;  // e.g., "192.168.1.100:4370"
  
  // Send request to Flask backend
  const res = await fetch("/connect", {
    method: "POST",
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ip: selectedDevice })
  });
}
```

### 2. Flask Backend Receives Request

```
[Browser] → POST /connect → [Flask Server]
```

**Backend Code** (`app.py`):
```python
@app.route('/connect', methods=['POST'])
def connect():
    data = request.json
    ip = data.get('ip')  # e.g., "192.168.1.100:4370"
    
    # Parse IP and port
    parts = ip.split(':')
    host = parts[0]      # "192.168.1.100"
    port = int(parts[1]) if len(parts) > 1 else 4370  # 4370 (default ZKTeco port)
```

### 3. Flask Connects to ZKTeco Device

```
[Flask Server] → TCP/IP Connection → [ZKTeco Device at 192.168.1.100:4370]
```

**Connection Process**:
```python
# Create ZK client object
zk = ZK(host, port=port, timeout=10)

# Establish TCP/IP connection to device
conn = zk.connect()  # ← This opens a socket connection to the device
```

**What happens:**
- Flask opens a **TCP socket** to the device's IP address
- Uses ZKTeco's proprietary protocol on port **4370** (default)
- The `pyzk` library handles the low-level protocol communication
- Device must be on the same network or accessible via port forwarding

### 4. Fetch User List from Device

```
[Flask Server] ← Request Users ← [ZKTeco Device]
```

**Code**:
```python
users = []
for user in conn.get_users():  # ← Requests list of all users from device
    users.append({
        'uid': user.uid,
        'user_id': user.user_id,
        'name': user.name,
        'privilege': user.privilege,
        # ... etc
    })
```

**What this does:**
- Sends a command to the device: "Give me all registered users"
- Device responds with user data (IDs, names, etc.)
- This **proves the connection works** and shows device has users

### 5. Disconnect and Return Response

```
[Flask Server] → Disconnect → [ZKTeco Device]
[Flask Server] → JSON Response → [Browser]
```

**Code**:
```python
finally:
    if conn:
        conn.disconnect()  # ← Close the connection

return jsonify({
    'message': 'Successfully connected to device',
    'users': users  # List of users from device
})
```

### 6. Frontend Updates UI

```
[Browser] ← Receives Response ← [Flask Server]
```

**Frontend Code**:
```javascript
if (result.users) {
    // Show date selection form
    document.getElementById("dateSection").classList.remove("hidden");
    
    // Update button to show "Connected!"
    btnText.textContent = "Connected!";
    btn.disabled = true;
    
    toastifyMsg("Connected to device!", "success");
}
```

---

## Visual Diagram

```
┌─────────────┐
│   Browser   │
│  (Frontend) │
└──────┬──────┘
       │ 1. User clicks "Connect"
       │    POST /connect {ip: "192.168.1.100:4370"}
       ▼
┌─────────────────┐
│  Flask Server    │
│  (Your App)      │
└──────┬───────────┘
       │ 2. Parse IP:port
       │    host = "192.168.1.100"
       │    port = 4370
       │
       │ 3. Create ZK client
       │    zk = ZK(host, port)
       │
       │ 4. Connect to device
       │    conn = zk.connect()
       │    ────────────────────┐
       │                        │ TCP/IP Socket
       │                        │ (Port 4370)
       │                        ▼
       │              ┌──────────────────┐
       │              │  ZKTeco Device   │
       │              │ 192.168.1.100    │
       │              │   Port 4370      │
       │              └──────────────────┘
       │                        │
       │ 5. Request users       │
       │    users = conn.get_users()
       │                        │
       │ 6. Device responds     │
       │    with user list      │
       │                        │
       │ 7. Disconnect          │
       │    conn.disconnect()   │
       │                        │
       │ 8. Return JSON         │
       │    {users: [...]}      │
       ▼
┌─────────────┐
│   Browser   │
│  (Frontend) │
│ Shows users │
│ & date form │
└─────────────┘
```

---

## Technical Details

### Protocol Used
- **Protocol**: ZKTeco proprietary TCP/IP protocol
- **Port**: 4370 (default ZKTeco communication port)
- **Library**: `pyzk` (Python ZKTeco library)
- **Connection Type**: Direct TCP socket connection

### Network Requirements

**For Same Network:**
```
Your Computer → Same WiFi/LAN → ZKTeco Device
✅ Works automatically
```

**For Different Networks:**
```
Your Computer → Internet → Router → Port Forward → ZKTeco Device
❌ Requires port forwarding (complex and insecure)
```

### Connection Lifecycle

1. **Connect**: Opens TCP socket to device
2. **Authenticate**: Device may require password (default: 0)
3. **Query**: Request data (users, attendance, etc.)
4. **Disconnect**: Close socket connection

**Important**: Connection is **not persistent** - it connects, gets data, then disconnects immediately.

---

## Comparison: Pull SDK vs Push SDK (ADMS)

| Aspect | Pull SDK (Current "Connect") | Push SDK (ADMS) |
|--------|------------------------------|-----------------|
| **Who Initiates** | Your server → Device | Device → Your server |
| **When** | When you click button | Automatically on each punch |
| **Connection** | Temporary (connect → query → disconnect) | Device pushes data via HTTP |
| **Network** | Same network or port forwarding | Any network with internet |
| **Real-time** | No (manual fetch) | Yes (instant push) |
| **Use Case** | Manual data retrieval | Automatic real-time sync |

---

## What Happens After "Connect"

After successfully connecting:

1. **Date Selection Form Appears**
   - You can select start and end dates
   - This is for fetching historical attendance data

2. **"Fetch & Send" Button Becomes Available**
   - When clicked, it:
     - Connects to device again
     - Fetches attendance records for selected date range
     - Uploads them to your HRMS backend
     - Shows results in a table

3. **Connection is Not Maintained**
   - The connection closes immediately after getting users
   - Each "Fetch & Send" creates a new connection

---

## Why This Method Has Limitations

1. **Network Dependency**
   - Device must be on same network
   - Or requires complex port forwarding setup

2. **Manual Process**
   - You must click "Connect" and "Fetch & Send" manually
   - Not automatic

3. **Not Real-Time**
   - Data is only fetched when you manually request it
   - Misses punches that happen between fetches

4. **Multiple Locations**
   - Difficult to manage devices across different offices
   - Each location needs separate connection setup

---

## This is Why ADMS (Push SDK) is Better

The ADMS method we added solves these issues:

- ✅ **Automatic**: Device pushes data immediately when someone punches
- ✅ **Cross-Network**: Works from any location with internet
- ✅ **Real-Time**: Data arrives instantly
- ✅ **No Manual Steps**: Fully automated

**But** the "Connect" button (Pull SDK) is still useful for:
- Testing device connectivity
- Manual data retrieval
- Backing up data
- Initial setup and verification

---

## Summary

The "Connect" button:
1. Takes device IP from dropdown
2. Flask server opens TCP connection to device (port 4370)
3. Requests list of users from device
4. Disconnects
5. Shows success if connection worked

This is the **Pull SDK** method - your server pulls data from the device when you request it.

The **ADMS (Push SDK)** method is different - the device automatically pushes data to your server whenever someone punches in/out, without you needing to click anything.

