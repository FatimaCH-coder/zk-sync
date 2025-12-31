# ZKTeco Attendance Uploader

A cross-platform desktop app to fetch, view, and upload attendance records from ZKTeco devices, with a modern web UI and easy exit functionality.

---

## Project Directory Structure

```
zk-sync/
├── app.py                # Main Flask application
├── README.md             # Project documentation
├── requirements.txt      # Python dependencies
├── templates/
│   └── index.html        # Frontend HTML (TailwindCSS + Toastify)
├── venv/                 # Python virtual environment (not tracked in git)
├── zk_utils.py           # ZKTeco device utility functions
└── ...                   # Other files
```

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/code-huddle-abdur-rehman/zk-sync.git
cd zk-sync
```

### 2. Create and Activate a Virtual Environment

#### **Windows**

```bash
python -m venv venv
venv\Scripts\activate
```

#### **Mac/Linux**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Running the App

### Development Mode (with Auto-Reload)

For development with automatic code reloading (like `npm run start:dev` in NestJS):

1. **Add to your `.env` file:**
   ```env
   FLASK_DEBUG=True
   # or
   FLASK_ENV=development
   ```

2. **Run the app:**
   ```bash
   python app.py
   ```

3. **Features:**
   - ✅ Auto-reloads when you change code files
   - ✅ Better error messages with stack traces
   - ✅ Debug mode enabled
   - ✅ Browser opens automatically

### Production Mode

For production (no auto-reload):

1. **Make sure `.env` has:**
   ```env
   FLASK_DEBUG=False
   # or omit FLASK_DEBUG entirely
   ```

2. **Run the app:**
   ```bash
   python app.py
   ```

### Manual Port Configuration

You can set a custom port in `.env`:
```env
FLASK_PORT=5000
```

**Note:** 
- The app will open in your default browser at [http://localhost:5000](http://localhost:5000)
- Use the web interface to connect to your ZKTeco device, fetch attendance, and upload records.
- To exit, click the red **Exit Application** button in the UI.
- In development mode, press `Ctrl+C` in the terminal to stop the server.

---

## Building Standalone Executables

### **Windows Build**

1. **Install PyInstaller**
   ```bash
   pip install pyinstaller
   ```
2. **Build the .exe**
   ```bash
   pyinstaller --onefile --windowed --add-data "templates;templates" app.py
   ```
   - The built executable will be in the `dist/` folder as `app.exe`.
   - Double-click `app.exe` to run. The app will open in your browser, and no terminal window will appear.

### **Mac Build**

1. **Build on a Mac (cannot cross-compile from Windows)**
2. **Install PyInstaller**
   ```bash
   pip install pyinstaller
   ```
3. **Build the .app bundle**
   ```bash
   pyinstaller --onefile --windowed --add-data "templates:templates" app.py
   ```
   - The built app will be in the `dist/` folder as `app.app`.
   - Double-click `app.app` to run. The app will open in your browser, and no terminal window will appear.
4. **Mac 4. Mac-Specific Considerations**
   - App Bundle vs Executable
      - PyInstaller creates a .app bundle in the dist folder
      - Users can double-click the .app file to run it
      - The .app file is actually a folder (right-click → "Show Package Contents" to see inside)
   
   - Gatekeeper Security
      - Mac may block the app due to security settings
      - Users may need to right-click → "Open" the first time
      - Or go to System Preferences → Security & Privacy → "Allow apps from anywhere"

#### **Optional: Create a DMG for Distribution**

```bash
brew install create-dmg
create-dmg --volname "ZKTeco Attendance Uploader" --window-pos 200 120 --window-size 600 300 --icon-size 100 --icon "app.app" 175 120 --hide-extension "app.app" --app-drop-link 425 120 "ZKTeco-Attendance-Uploader.dmg" "dist/"
```

---

## Notes

- **You must build on each target OS** (Windows for .exe, Mac for .app).
- The `--add-data` flag uses `;` on Windows and `:` on Mac/Linux.
- The app will open in your default browser and can be exited using the **Exit Application** button.
- If you see any issues with missing dependencies, ensure your virtual environment is activated and all requirements are installed.

---

## Usage

### Pull SDK Method (Traditional - Current Default)

1. **Connect to Device:** Enter the device IP and click Connect.
2. **Select Date Range:** Choose start and end dates.
3. **Fetch & Send:** Click to fetch attendance and upload to your backend.
4. **View Records:** Attendance records are shown in a table.
5. **Exit:** Click the red Exit Application button to close the app and server.

### Push SDK Method (ADMS - Recommended for Multiple Networks)

The Push SDK (ADMS) method allows ZKTeco devices to automatically send attendance data to your server in real-time. This is **highly recommended** for:
- Multiple office locations across different networks
- Real-time attendance tracking
- No need for port forwarding or complex network configuration
- Better scalability and reliability

#### ADMS Setup Instructions

1. **Deploy Your Application**
   - Deploy this Flask application to a cloud server with a public IP/domain (e.g., AWS, Digital Ocean, Heroku, or your own server)
   - Ensure the server is accessible via HTTPS (recommended) or HTTP
   - Note the public URL (e.g., `https://your-server.com`)

2. **Configure Environment Variables**
   Add these to your `.env` file:
   ```env
   # ADMS Configuration
   ADMS_API_KEY=your-secure-api-key-here  # Optional but recommended for security
   ADMS_DEFAULT_ENV=dev  # or 'prod' - default environment for ADMS uploads
   ADMS_SERVICE_TOKEN=your-backend-service-token  # Optional: token for backend authentication
   ```

3. **Configure ZKTeco Device (F-22 or compatible)**
   - Access your ZKTeco device's web interface or use the device menu
   - Navigate to **Network Settings** → **ADMS** (Attendance Management Data Service)
   - Enable ADMS
   - Set the **ADMS Server URL** to: `http://your-server.com:5000/adms/webhook`
     - For HTTPS: `https://your-server.com/adms/webhook`
   - If you configured `ADMS_API_KEY`, add it as a query parameter or header:
     - URL format: `http://your-server.com:5000/adms/webhook?api_key=your-secure-api-key-here`
   - Save the configuration

4. **Test the Connection**
   - Visit `http://your-server.com:5000/adms/status` to verify the endpoint is active
   - Make a test punch on the device
   - Check the server logs to confirm data is being received
   - Verify the data appears in your HRMS backend

#### ADMS Webhook Endpoint

- **URL:** `/adms/webhook`
- **Methods:** `POST`, `GET`
- **Authentication:** Optional API key via `X-API-Key` header or `api_key` query parameter
- **Data Format:** Accepts multiple ZKTeco ADMS data formats automatically

#### ADMS vs Pull SDK Comparison

| Feature | Pull SDK (Current) | Push SDK (ADMS) |
|---------|-------------------|-----------------|
| **Network Setup** | Requires port forwarding for remote devices | Works across any network with internet |
| **Real-Time** | No (periodic polling) | Yes (instant push) |
| **Scalability** | Limited by polling frequency | Excellent (device-initiated) |
| **Server Load** | High (constant polling) | Low (only on events) |
| **Best For** | Single location, local network | Multiple locations, distributed networks |

#### ADMS Data Flow

```
ZKTeco Device → Internet → Your Server (/adms/webhook) → HRMS Backend → MongoDB
```

The device automatically pushes attendance data whenever an employee checks in/out, eliminating the need for manual fetching or scheduled polling.

---
