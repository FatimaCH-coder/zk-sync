# Quick Test Guide - iClock Protocol

Your device is already configured! Here's how to test it.

## ✅ What's Already Done

1. ✅ Endpoints added: `/iclock/getrequest` and `/iclock/cdata`
2. ✅ Tabulate library installed
3. ✅ Device configured with your IP and port 5000

## 🚀 Start the Server

```bash
cd zk-sync
source venv/Scripts/activate  # Windows Git Bash
python app.py
```

You should see:
```
🚀 Flask running in DEVELOPMENT mode with auto-reload enabled
🌐 Server accessible at: http://0.0.0.0:5000
   ✅ Devices on your network can connect to this server
 * Running on http://0.0.0.0:5000
```

## 📡 What to Watch For

### 1. Heartbeat (Within 1 minute)

The device will ping your server every 30-60 seconds. You should see:

```
💓 [2025-12-30 15:30:45] HEARTBEAT from Device
   📱 Serial Number: ABC123456
   📍 Device IP: 192.168.1.100
   ✅ Device is alive and connected
```

**If you don't see this:**
- Check Windows Firewall (allow port 5000)
- Verify device IP matches your computer's IP
- Check device and computer are on same network

### 2. Test Punch (Scan Fingerprint/Card)

When you scan your fingerprint or card, you should immediately see:

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

## 🔧 Troubleshooting

### No Heartbeat Received

**Check 1: Windows Firewall**
```bash
# Allow port 5000
netsh advfirewall firewall add rule name="Flask iClock" dir=in action=allow protocol=TCP localport=5000
```

**Check 2: Verify Your IP**
```bash
ipconfig
# Look for IPv4 Address (e.g., 192.168.1.15)
# Make sure device Server Address matches this
```

**Check 3: Network Connection**
- Device and computer must be on same WiFi/LAN
- Try pinging device from computer: `ping 192.168.1.100` (device IP)

### Heartbeat Works But No Data

**Check 1: Device Settings**
- Make sure "Real-time Upload" or "Push Mode" is enabled
- Verify device has attendance records to send

**Check 2: Make a Test Punch**
- Scan your fingerprint or card
- Data should appear immediately

### Data Received But Format Wrong

Check the "RAW DATA RECEIVED" section. It should look like:
```
123	2025-12-30 15:31:20	0	15	0
```

If format is different, the parser might need adjustment.

## 📝 Expected Output Format

**Raw Data:**
```
USERID \t TIMESTAMP \t STATUS \t VERIFY \t WORKCODE
```

**Example:**
```
123	2025-12-30 15:31:20	0	15	0
456	2025-12-30 15:32:10	1	15	0
```

**Field Meanings:**
- **USERID**: Employee ID
- **TIMESTAMP**: Date and time (YYYY-MM-DD HH:MM:SS)
- **STATUS**: 0 = Check In, 1 = Check Out
- **VERIFY**: 15 = Fingerprint, 1 = Password, etc.
- **WORKCODE**: Usually 0

## 🎯 Success Indicators

✅ **Heartbeat appears every 30-60 seconds**
✅ **Data appears immediately when you punch**
✅ **Table displays formatted data**
✅ **Backend upload works (if configured)**

## 🔄 Next Steps

Once you see data coming through:

1. **Configure Backend Upload** (optional):
   - Add `DEV_BACKEND_URL` to `.env`
   - Add `ADMS_SERVICE_TOKEN` to `.env`
   - Data will auto-upload to your HRMS

2. **Monitor Logs**:
   - Watch console for all punches
   - Check for any errors

3. **Production Setup**:
   - Deploy to cloud server
   - Update device with public URL
   - Use HTTPS for security

---

**Ready to test!** Start the server and wait for the heartbeat. Then make a test punch! 🎉

