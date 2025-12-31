# Network Switching Solutions for ZKTeco Devices

## The Problem

When you configure your ZKTeco device with a local IP address (e.g., `192.168.1.15:5000`), it works perfectly **as long as you're on the same network**. However, when you switch networks (different WiFi, mobile hotspot, etc.), your computer gets a **different IP address**, and the device can no longer connect.

**Example:**
- **Network 1**: Your computer is `192.168.1.15`
- **Network 2**: Your computer is `192.168.0.20` (different network)
- **Device**: Still trying to connect to `192.168.1.15` ❌

## Solutions

### Solution 1: Use ngrok (Recommended for Testing) ⭐

**ngrok** creates a **public URL** that tunnels to your local server. This URL works from **any network** and never changes (until you restart ngrok).

#### Step 1: Install ngrok

```bash
# Install pyngrok (Python wrapper)
pip install pyngrok

# OR install ngrok directly:
# Windows: Download from https://ngrok.com/download
# Mac: brew install ngrok
# Linux: Download from https://ngrok.com/download
```

#### Step 2: Get ngrok Auth Token (Optional but Recommended)

1. Sign up at https://ngrok.com (free account)
2. Get your auth token from the dashboard
3. Add to `.env`:
   ```env
   NGROK_AUTH_TOKEN=your-ngrok-auth-token-here
   ENABLE_NGROK=True
   ```

#### Step 3: Start Flask with ngrok

When you run `python app.py`, ngrok will automatically start and show you a public URL:

```
🌍 NGROK TUNNEL ACTIVE
================================================================================
🔗 Public URL: https://abc123.ngrok.io
   📍 Heartbeat: https://abc123.ngrok.io/iclock/getrequest
   📍 Data: https://abc123.ngrok.io/iclock/cdata

💡 Configure your device Server Address to:
   abc123.ngrok.io:443
   (Remove http:// or https:// prefix)

✅ This URL works from ANY network!
================================================================================
```

#### Step 4: Configure Device

On your ZKTeco device:
1. **Server Address**: `abc123.ngrok.io` (without http://)
2. **Server Port**: `443` (for HTTPS) or `80` (for HTTP)
3. **HTTPS**: **ON** (if using port 443)

**Note:** The ngrok URL changes each time you restart ngrok (unless you have a paid plan with a static domain).

#### Advantages:
- ✅ Works from any network
- ✅ No router configuration needed
- ✅ Free tier available
- ✅ Automatic HTTPS

#### Disadvantages:
- ⚠️ URL changes on restart (free tier)
- ⚠️ Requires internet connection
- ⚠️ Free tier has connection limits

---

### Solution 2: Check Current IP When Switching Networks

If you prefer to use local IP addresses, you can check your current IP each time you switch networks.

#### Method 1: Use the API Endpoint

Visit: `http://localhost:5000/network/ip`

This will show:
```json
{
  "local_ip": "192.168.0.20",
  "port": 5000,
  "server_url": "http://192.168.0.20:5000",
  "iclock_heartbeat": "http://192.168.0.20:5000/iclock/getrequest",
  "iclock_data": "http://192.168.0.20:5000/iclock/cdata",
  "message": "Configure your device Server Address to: 192.168.0.20",
  "note": "This IP changes when you switch networks. Use ngrok for a permanent URL."
}
```

#### Method 2: Check Console Output

When you start Flask, it automatically shows your current IP:

```
🌐 Server accessible at: http://0.0.0.0:5000
   📍 Your local IP: 192.168.0.20
   🔗 Device Server Address: 192.168.0.20:5000
   ✅ Devices on your network can connect to this server
   ⚠️  NOTE: This IP changes when you switch networks!
```

#### Method 3: Command Line

**Windows:**
```bash
ipconfig
# Look for "IPv4 Address" under your active network adapter
```

**Mac/Linux:**
```bash
ifconfig
# or
ip addr
# Look for inet address (usually 192.168.x.x)
```

Then update your device configuration with the new IP.

#### Advantages:
- ✅ No external services needed
- ✅ Works offline
- ✅ No connection limits

#### Disadvantages:
- ⚠️ Must reconfigure device each time you switch networks
- ⚠️ Only works on same local network

---

### Solution 3: Use a Cloud Server (Production)

For production use, deploy your Flask app to a cloud server with a **static IP address** or **domain name**.

**Options:**
- **Heroku**: `https://your-app.herokuapp.com`
- **AWS EC2**: Static IP or Elastic IP
- **DigitalOcean**: Droplet with static IP
- **Azure**: App Service with custom domain
- **Google Cloud**: Compute Engine with static IP

Then configure your device with the cloud server URL.

#### Advantages:
- ✅ Permanent URL/IP
- ✅ Works from anywhere
- ✅ Professional solution
- ✅ Better security

#### Disadvantages:
- ⚠️ Requires deployment setup
- ⚠️ May have costs
- ⚠️ More complex setup

---

### Solution 4: Use Dynamic DNS (Advanced)

If you have a router that supports Dynamic DNS (DDNS), you can set up a domain name that automatically updates when your IP changes.

**Services:**
- No-IP (https://www.noip.com)
- DuckDNS (https://www.duckdns.org)
- Dynu (https://www.dynu.com)

**Setup:**
1. Sign up for a DDNS service
2. Configure your router with DDNS credentials
3. Get a domain like `yourname.ddns.net`
4. Configure device with `yourname.ddns.net:5000`

#### Advantages:
- ✅ Permanent domain name
- ✅ Works from home/office
- ✅ Free options available

#### Disadvantages:
- ⚠️ Requires router support
- ⚠️ May not work on all networks
- ⚠️ Setup complexity

---

## Quick Comparison

| Solution | Works Anywhere | Setup Difficulty | Cost | Best For |
|----------|---------------|------------------|------|----------|
| **ngrok** | ✅ Yes | 🟢 Easy | Free/Paid | Testing, Development |
| **Check IP** | ❌ Same network only | 🟢 Very Easy | Free | Local testing |
| **Cloud Server** | ✅ Yes | 🟡 Medium | Paid | Production |
| **Dynamic DNS** | ⚠️ Depends | 🔴 Complex | Free/Paid | Home/Office |

---

## Recommended Setup for Testing

1. **Use ngrok** for testing across different networks
2. Add to `.env`:
   ```env
   ENABLE_NGROK=True
   NGROK_AUTH_TOKEN=your-token-here  # Optional but recommended
   ```
3. Start Flask: `python app.py`
4. Copy the ngrok URL shown in console
5. Configure device with ngrok URL

## Recommended Setup for Production

1. Deploy Flask app to cloud server (Heroku, AWS, etc.)
2. Get permanent URL/IP
3. Configure device with cloud server URL
4. Set up HTTPS for security

---

## Troubleshooting

### Problem: ngrok URL not showing

**Solutions:**
1. Check `ENABLE_NGROK=True` in `.env`
2. Install pyngrok: `pip install pyngrok`
3. Check ngrok auth token is valid (if using)

### Problem: Device can't connect to ngrok URL

**Solutions:**
1. Make sure device has internet connection
2. Check device Server Port matches ngrok port (443 for HTTPS, 80 for HTTP)
3. Verify HTTPS setting on device matches ngrok (HTTPS = ON for port 443)
4. Try HTTP instead of HTTPS if device doesn't support it

### Problem: IP address changes frequently

**Solutions:**
1. Use ngrok for permanent URL
2. Set static IP on your computer (advanced)
3. Use cloud server deployment

---

## Additional Notes

- The `/network/ip` endpoint is always available to check your current IP
- Flask automatically shows your local IP when starting
- ngrok free tier has connection limits (40 connections/minute)
- For production, always use HTTPS and proper authentication

---

**Need help?** Check the console output when starting Flask - it shows all connection information!

