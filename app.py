# app.py
import webview
import webbrowser
import threading
from zk import ZK
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from zk_utils import fetch_attendance
from datetime import datetime, timedelta
import requests
import os
from dotenv import load_dotenv
import jwt
from functools import wraps
import socket

# Load environment variables
load_dotenv()

# Track server start time to filter out old records
SERVER_START_TIME = datetime.now()

# Check if .env file exists
env_path = '.env'
if os.path.exists(env_path):
    print(f".env file found at: {os.path.abspath(env_path)}")
else:
  print(f".env file NOT found at: {os.path.abspath(env_path)}")
  # Try to find it in the bundle directory
  bundle_dir = os.path.dirname(os.path.abspath(__file__))
  bundle_env_path = os.path.join(bundle_dir, '.env')
  if os.path.exists(bundle_env_path):
    print(f".env file found in bundle at: {bundle_env_path}")
    load_dotenv(bundle_env_path)
  else:
    print(f".env file not found anywhere!")

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')  # Add a secret key for sessions

# Configure session to be more persistent
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours

# Authentication decorator
def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # For now, we'll use a simple session check
        # In production, you might want to validate JWT tokens
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    # Redirect to login if not authenticated, otherwise to dashboard
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login_post():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')
    environment = data.get('environment', 'dev')
    
    if not email or not password or not role:
        return jsonify({'error': 'Email, password, and role are required'}), 400
    
        # Determine backend URL based on environment
    if environment == 'prod':
        backend_url = os.getenv('PROD_BACKEND_URL', 'http://localhost:3001')
        print(f"Using production backend URL: {backend_url}")
    else:
        backend_url = os.getenv('DEV_BACKEND_URL', 'https://code-huddle-hrms-dev-61ae656862e5.herokuapp.com')
    
    # Ensure proper URL construction by removing trailing slash if present
    backend_url = backend_url.rstrip('/')
    login_url = f"{backend_url}/auth/login"
    
    
    # Call the main backend's login endpoint
    try:
        login_response = requests.post(
            login_url,
            json={
                'email': email,
                'password': password,
                'role': role
            },
            headers={
                'Content-Type': 'application/json',
                'x-tenant': 'default'  # Add required tenant header
            },
            timeout=10
        )
        
        
        if login_response.status_code in [200, 201]:
            try:
                login_data = login_response.json()
                
                
                # Try to extract tokens from different possible formats
                tokens = {}
                
                # Check if tokens exist in the response
                if 'tokens' in login_data and login_data['tokens']:
                    tokens_data = login_data['tokens']
                    
                    # Check for snake_case format first (most common)
                    if 'access_token' in tokens_data:
                        tokens = {
                            'accessToken': tokens_data.get('access_token'),
                            'refreshToken': tokens_data.get('refresh_token', '')
                        }
                    
                    # Check for camelCase format
                    elif 'accessToken' in tokens_data:
                        tokens = tokens_data
                
                # Format 3: Direct access_token field
                elif 'access_token' in login_data:
                    tokens = {
                        'accessToken': login_data.get('access_token'),
                        'refreshToken': login_data.get('refresh_token', '')
                    }
                
                # Format 4: accessToken field
                elif 'accessToken' in login_data:
                    tokens = {
                        'accessToken': login_data.get('accessToken'),
                        'refreshToken': login_data.get('refreshToken', '')
                    }
                
                # Format 5: Check if tokens are in data field
                elif 'data' in login_data and 'tokens' in login_data['data']:
                    tokens = login_data['data']['tokens']
                
                # Store user info in session
                session['user_id'] = login_data.get('user', {}).get('_id')
                session['user_email'] = login_data.get('user', {}).get('email')
                session['user_role'] = login_data.get('user', {}).get('role')
                session['environment'] = environment
                session['tokens'] = tokens  # Store tokens in session
                session.permanent = True  # Make session permanent
                
                
                return jsonify({
                    'success': True,
                    'tokens': login_data.get('tokens', {}),
                    'user': login_data.get('user', {})
                })
            except Exception as e:
                return jsonify({
                    'error': 'Invalid response format from backend'
                }), 500
        else:
            try:
                error_data = login_response.json() if login_response.content else {}
            except:
                error_data = {}
            
            return jsonify({
                'error': f'Login failed with status {login_response.status_code}'
            }), login_response.status_code
            
    except requests.exceptions.RequestException as e:
        return jsonify({
            'error': f'Failed to connect to {environment} backend: {str(e)}'
        }), 500

@app.route('/debug-session')
def debug_session():
    """Debug endpoint to check session state"""
    return jsonify({
        'session_data': dict(session),
        'session_permanent': session.permanent,
        'user_id': session.get('user_id'),
        'tokens': session.get('tokens', {}),
        'environment': session.get('environment')
    })

@app.route('/test-session', methods=['POST'])
def test_session():
    """Test endpoint to manually set session data"""
    session['test_token'] = 'test_value_123'
    session['tokens'] = {'accessToken': 'test_access_token', 'refreshToken': 'test_refresh_token'}
    session.permanent = True
    return jsonify({'message': 'Session test data set', 'session': dict(session)})

@app.route('/set-token', methods=['POST'])
def set_token():
    """Manual endpoint to set access token for testing"""
    data = request.json
    access_token = data.get('accessToken') or data.get('access_token')
    
    if access_token:
        session['tokens'] = {
            'accessToken': access_token,
            'refreshToken': data.get('refreshToken', data.get('refresh_token', ''))
        }
        session.permanent = True
        return jsonify({
            'message': 'Token set successfully',
            'session': dict(session)
        })
    else:
        return jsonify({'error': 'No access token provided'}), 400

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/devices', methods=['GET'])
@require_auth
def get_devices():
    """Get list of available devices from .env file"""
    devices = []
    for i in range(1, 3):  # DEVICE_IP_1 and DEVICE_IP_2
        device_ip = os.getenv(f'DEVICE_IP_{i}')
        if device_ip:
            devices.append(device_ip)
    return jsonify({'devices': devices})

@app.route('/hrms-urls', methods=['GET'])
@require_auth
def get_hrms_urls():
    """Get HRMS URLs for different environments"""
    dev_hrms_url = os.getenv('DEV_HRMS_URL', 'https://dev-hrms.yourcompany.com')
    prod_hrms_url = os.getenv('PROD_HRMS_URL', 'https://hrms.yourcompany.com')
    
    return jsonify({
        'dev': dev_hrms_url,
        'prod': prod_hrms_url
    })

@app.route('/connect', methods=['POST'])
@require_auth
def connect():
    data = request.json
    ip = data.get('ip')
    if not ip:
        return jsonify({'error': 'IP address is required'}), 400

    parts = ip.split(':')
    host = parts[0]
    port = int(parts[1]) if len(parts) > 1 else 4370

    zk = ZK(host, port=port, timeout=10)
    conn = None
    try:
        conn = zk.connect()
        users = []
        for user in conn.get_users():
            users.append({
                'uid': user.uid,
                'user_id': user.user_id,
                'name': user.name,
                'privilege': user.privilege,
                'password': user.password,
                'group_id': user.group_id,
                # add more fields as needed
            })
        return jsonify({
            'message': 'Successfully connected to device',
            'users': users
        })
    except Exception as e:
        return jsonify({'error': str(e) or 'Failed to connect to ZKTeco device'}), 500
    finally:
        if conn:
            conn.disconnect()

@app.route('/attendance', methods=['POST'])
@require_auth
def attendance():
    data = request.json
    ip = data.get('ip')
    start_date = data.get('startDate')
    end_date = data.get('endDate')
    environment = data.get('environment', 'dev')  # Default to dev if not specified
    
    if not ip:
        return jsonify({'error': 'IP address is required'}), 400

    parts = ip.split(':')
    host = parts[0]
    port = int(parts[1]) if len(parts) > 1 else 4370

    zk = ZK(host, port=port, timeout=10)
    conn = None
    try:
        conn = zk.connect()
        users = conn.get_users()
        user_map = {str(user.user_id): user.name for user in users}
        attendance = conn.get_attendance()
    except Exception as e:
        return jsonify({'error': str(e) or 'Failed to connect to ZKTeco device'}), 500
    finally:
        try:
            if conn:
                conn.disconnect()
        except Exception:
            pass

    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1) - timedelta(milliseconds=1)

    logs = []
    for a in attendance:
        if start <= a.timestamp <= end:
            # punch: 0 = check in, 1 = check out (typical for ZKTeco)
            status = 'Check In' if getattr(a, 'punch', 0) == 0 else 'Check Out'
            logs.append({
                'user_id': a.user_id,
                'name': user_map.get(str(a.user_id), f'User {a.user_id}'),
                'number': str(a.user_id),
                'dateTime': a.timestamp.isoformat(),
                'status': status
            })

    # Prepare data for forwarding (remove user_id, keep only required fields)
    upload_data = [
        {
            'dateTime': log['dateTime'],
            'name': log['name'],
            'status': log['status'],
            'number': log['number']
        }
        for log in logs
    ]

    # Determine backend endpoint based on environment from .env file
    if environment == 'prod':
        backend_url = os.getenv('PROD_BACKEND_URL', 'http://localhost:3001')
        print(f"Using production backend URL: {backend_url}")
    else:
        backend_url = os.getenv('DEV_BACKEND_URL', 'https://code-huddle-hrms-dev-61ae656862e5.herokuapp.com')

    backend_url = backend_url.rstrip('/')
    upload_url = f"{backend_url}/attendance/upload"

    # Get tokens from session
    tokens = session.get('tokens', {})
    access_token = tokens.get('accessToken') or tokens.get('access_token')
    
    
    # Prepare headers with authentication
    headers = {
        'Content-Type': 'application/json',
        'x-tenant': 'default'  # Add required tenant header
    }
    
    if access_token:
        headers['Authorization'] = f'Bearer {access_token}'

    # Forward to external backend
    try:
        upload_response = requests.post(
            upload_url,
            json=upload_data,
            headers=headers,
            timeout=60
        )
        
        upload_response.raise_for_status()
        upload_result = upload_response.json() if upload_response.content else {'success': True}
    except Exception as e:
        return jsonify({
            'attendance': {
                'logs': logs,
                'userMap': user_map,
            },
            'upload': {
                'success': False,
                'error': f'Failed to upload to {environment} backend: {str(e)}'
            }
        }), 200

    return jsonify({
        'attendance': {
            'logs': logs,
            'userMap': user_map,
        },
        'upload': {
            'success': True,
            'result': upload_result,
            'environment': environment
        }
    })

@app.route('/adms/webhook', methods=['POST', 'GET'])
def adms_webhook():
    """
    ADMS (Push SDK) webhook endpoint to receive real-time attendance data from ZKTeco devices.
    This endpoint is called automatically by the device when attendance is recorded.
    No authentication required for device push, but can be secured with API key validation.
    """
    # Get current timestamp for logging
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Get API key from environment for device authentication (optional but recommended)
    adms_api_key = os.getenv('ADMS_API_KEY', '')
    
    # Get device IP from request (for logging/validation)
    device_ip = request.remote_addr
    device_ip_header = request.headers.get('X-Forwarded-For', device_ip)
    
    # Log incoming request
    print(f"\n{'='*80}")
    print(f"🔔 [{current_time}] ADMS WEBHOOK - New Request Received")
    print(f"{'='*80}")
    print(f"📍 Device IP: {device_ip_header}")
    print(f"🌐 Method: {request.method}")
    print(f"🔗 URL: {request.url}")
    print(f"📋 Headers: {dict(request.headers)}")
    
    # Validate API key if configured
    if adms_api_key:
        provided_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        if provided_key != adms_api_key:
            print(f"❌ Authentication Failed: Invalid API key")
            print(f"{'='*80}\n")
            return jsonify({'error': 'Invalid API key'}), 401
        else:
            print(f"✅ Authentication: API key validated")
    else:
        print(f"⚠️  Authentication: No API key configured (running without authentication)")
    
    try:
        # ZKTeco ADMS can send data in different formats
        # Try to parse JSON first (most common)
        if request.is_json:
            data = request.json
            print(f"📦 Data Format: JSON")
        # Try form data
        elif request.form:
            data = dict(request.form)
            print(f"📦 Data Format: Form Data")
        # Try query parameters (for GET requests)
        elif request.args:
            data = dict(request.args)
            print(f"📦 Data Format: Query Parameters")
        else:
            # Try to parse raw data
            raw_data = request.get_data(as_text=True)
            print(f"📦 Data Format: Raw Data")
            try:
                import json
                data = json.loads(raw_data) if raw_data else {}
            except:
                data = {}
        
        # Log raw received data
        print(f"📥 Raw Data Received:")
        print(f"   {data}")
        
        # Extract attendance data from various possible formats
        attendance_record = None
        print(f"\n🔍 Parsing attendance data...")
        
        # Format 1: Direct fields in JSON
        if 'user_id' in data or 'userId' in data or 'UserID' in data:
            print(f"   ✅ Detected Format 1: Direct fields in JSON")
            user_id = data.get('user_id') or data.get('userId') or data.get('UserID')
            timestamp_str = data.get('timestamp') or data.get('time') or data.get('datetime') or data.get('DateTime')
            punch = data.get('punch') or data.get('status') or data.get('Punch')
            name = data.get('name') or data.get('Name') or data.get('user_name')
            
            print(f"   👤 User ID: {user_id}")
            print(f"   📛 Name: {name or 'Not provided'}")
            print(f"   🕐 Timestamp String: {timestamp_str or 'Not provided'}")
            print(f"   👊 Punch Code: {punch}")
            
            # Parse timestamp
            if timestamp_str:
                try:
                    if isinstance(timestamp_str, str):
                        # Try ISO format first
                        try:
                            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        except:
                            # Try common formats
                            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y/%m/%d %H:%M:%S', '%d-%m-%Y %H:%M:%S']:
                                try:
                                    timestamp = datetime.strptime(timestamp_str, fmt)
                                    break
                                except:
                                    continue
                            else:
                                timestamp = datetime.now()
                                print(f"   ⚠️  Could not parse timestamp, using current time")
                    else:
                        timestamp = datetime.now()
                except:
                    timestamp = datetime.now()
                    print(f"   ⚠️  Error parsing timestamp, using current time")
            else:
                timestamp = datetime.now()
                print(f"   ⚠️  No timestamp provided, using current time")
            
            # Determine status
            if punch is not None:
                status = 'Check In' if int(punch) == 0 else 'Check Out'
            else:
                status = data.get('status', 'Check In')
            
            attendance_record = {
                'user_id': str(user_id),
                'number': str(user_id),
                'name': name or f'User {user_id}',
                'dateTime': timestamp.isoformat(),
                'status': status
            }
            
            print(f"   ✅ Parsed successfully!")
        
        # Format 2: Nested structure
        elif 'data' in data:
            print(f"   ✅ Detected Format 2: Nested structure")
            record_data = data['data']
            if isinstance(record_data, list) and len(record_data) > 0:
                record_data = record_data[0]
            
            user_id = record_data.get('user_id') or record_data.get('userId')
            timestamp_str = record_data.get('timestamp') or record_data.get('time')
            punch = record_data.get('punch') or record_data.get('status')
            name = record_data.get('name')
            
            print(f"   👤 User ID: {user_id}")
            print(f"   📛 Name: {name or 'Not provided'}")
            print(f"   🕐 Timestamp String: {timestamp_str or 'Not provided'}")
            print(f"   👊 Punch Code: {punch}")
            
            if user_id:
                timestamp = datetime.now()
                if timestamp_str:
                    try:
                        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    except:
                        print(f"   ⚠️  Could not parse timestamp, using current time")
                
                status = 'Check In' if (punch == 0 or punch == '0') else 'Check Out'
                
                attendance_record = {
                    'user_id': str(user_id),
                    'number': str(user_id),
                    'name': name or f'User {user_id}',
                    'dateTime': timestamp.isoformat(),
                    'status': status
                }
                
                print(f"   ✅ Parsed successfully!")
        
        # Format 3: Attendance log format
        elif 'attendance' in data:
            print(f"   ✅ Detected Format 3: Attendance log format")
            att_data = data['attendance']
            if isinstance(att_data, list) and len(att_data) > 0:
                att_data = att_data[0]
            
            user_id = att_data.get('user_id') or att_data.get('userId')
            timestamp_str = att_data.get('timestamp') or att_data.get('time')
            punch = att_data.get('punch')
            name = att_data.get('name')
            
            print(f"   👤 User ID: {user_id}")
            print(f"   📛 Name: {name or 'Not provided'}")
            print(f"   🕐 Timestamp String: {timestamp_str or 'Not provided'}")
            print(f"   👊 Punch Code: {punch}")
            
            if user_id:
                timestamp = datetime.now()
                if timestamp_str:
                    try:
                        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    except:
                        print(f"   ⚠️  Could not parse timestamp, using current time")
                
                status = 'Check In' if (punch == 0 or punch == '0') else 'Check Out'
                
                attendance_record = {
                    'user_id': str(user_id),
                    'number': str(user_id),
                    'name': name or f'User {user_id}',
                    'dateTime': timestamp.isoformat(),
                    'status': status
                }
                
                print(f"   ✅ Parsed successfully!")
        
        if not attendance_record:
            # Log the received data for debugging
            print(f"\n❌ ERROR: Could not parse attendance data")
            print(f"   Received data structure: {data}")
            print(f"   Available keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            print(f"{'='*80}\n")
            return jsonify({
                'error': 'Invalid data format',
                'received': data
            }), 400
        
        # Log parsed attendance record
        print(f"\n✅ ATTENDANCE RECORD PARSED:")
        print(f"   👤 User ID: {attendance_record['user_id']}")
        print(f"   📛 Name: {attendance_record['name']}")
        print(f"   🕐 Date/Time: {attendance_record['dateTime']}")
        print(f"   📍 Status: {attendance_record['status']}")
        
        # Determine environment (default to dev, can be overridden by device config)
        environment = data.get('environment', os.getenv('ADMS_DEFAULT_ENV', 'dev'))
        print(f"\n🌍 Environment: {environment.upper()}")
        
        # Prepare upload data
        upload_data = [{
            'dateTime': attendance_record['dateTime'],
            'name': attendance_record['name'],
            'status': attendance_record['status'],
            'number': attendance_record['number']
        }]
        
        # Determine backend endpoint
        if environment == 'prod':
            backend_url = os.getenv('PROD_BACKEND_URL', 'http://localhost:3001')
        else:
            backend_url = os.getenv('DEV_BACKEND_URL', 'https://code-huddle-hrms-dev-61ae656862e5.herokuapp.com')
        
        backend_url = backend_url.rstrip('/')
        upload_url = f"{backend_url}/attendance/upload"
        
        print(f"📤 Uploading to backend...")
        print(f"   URL: {upload_url}")
        
        # For ADMS, we might not have user session tokens
        # Option 1: Use a service account token from .env
        # Option 2: Allow unauthenticated uploads (if backend supports it)
        # Option 3: Use device-specific authentication
        
        service_token = os.getenv('ADMS_SERVICE_TOKEN', '')
        headers = {
            'Content-Type': 'application/json',
            'x-tenant': 'default'
        }
        
        if service_token:
            headers['Authorization'] = f'Bearer {service_token}'
            print(f"   🔐 Using service token for authentication")
        else:
            print(f"   ⚠️  No service token configured (upload may fail if backend requires auth)")
        
        # Forward to external backend
        try:
            upload_response = requests.post(
                upload_url,
                json=upload_data,
                headers=headers,
                timeout=10
            )
            
            upload_response.raise_for_status()
            upload_result = upload_response.json() if upload_response.content else {'success': True}
            
            print(f"\n✅ SUCCESS: Attendance uploaded to backend!")
            print(f"   Status Code: {upload_response.status_code}")
            print(f"   Response: {upload_result}")
            print(f"\n📊 SUMMARY:")
            print(f"   👤 Employee: {attendance_record['name']} (ID: {attendance_record['user_id']})")
            print(f"   🕐 Time: {attendance_record['dateTime']}")
            print(f"   📍 Action: {attendance_record['status']}")
            print(f"   🌍 Environment: {environment.upper()}")
            print(f"   📡 Device IP: {device_ip_header}")
            print(f"{'='*80}\n")
            
            return jsonify({
                'success': True,
                'message': 'Attendance recorded successfully',
                'data': attendance_record,
                'upload': upload_result
            }), 200
            
        except requests.exceptions.RequestException as e:
            print(f"\n❌ ERROR: Failed to upload to backend")
            print(f"   Error: {str(e)}")
            print(f"   URL: {upload_url}")
            print(f"   ⚠️  Data received but not uploaded (device will not retry)")
            print(f"\n📊 SUMMARY:")
            print(f"   👤 Employee: {attendance_record['name']} (ID: {attendance_record['user_id']})")
            print(f"   🕐 Time: {attendance_record['dateTime']}")
            print(f"   📍 Action: {attendance_record['status']}")
            print(f"   ❌ Upload Status: FAILED")
            print(f"{'='*80}\n")
            # Still return success to device so it doesn't retry
            # You might want to queue failed records for retry
            return jsonify({
                'success': True,  # Return success to device
                'message': 'Received but upload failed',
                'data': attendance_record,
                'error': str(e)
            }), 200
            
    except Exception as e:
        print(f"\n❌❌❌ CRITICAL ERROR in ADMS Webhook ❌❌❌")
        print(f"   Error Type: {type(e).__name__}")
        print(f"   Error Message: {str(e)}")
        print(f"   Device IP: {device_ip_header}")
        import traceback
        print(f"\n📋 Full Traceback:")
        traceback.print_exc()
        print(f"{'='*80}\n")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

# ============================================
# ZKTeco iClock/ADMS Protocol Endpoints
# ============================================
# These endpoints use the native ZKTeco iClock protocol
# Device sends plain text (tab-separated) data, not JSON

@app.route('/iclock/getrequest', methods=['GET'])
def iclock_getrequest():
    """
    Heartbeat endpoint - Device pings this every 30-60 seconds to say "I'm alive"
    This is the ZKTeco iClock protocol's keep-alive mechanism
    """
    # Silent heartbeat - device is just checking in, no need to log every time
    return "OK"

@app.route('/iclock/cdata', methods=['GET', 'POST'])
def iclock_cdata():
    """
    Data receiver endpoint - This is where punch logs actually arrive
    Device sends tab-separated plain text data (not JSON)
    Format: USERID \t TIMESTAMP \t STATUS \t VERIFY \t WORKCODE
    Only shows real-time data (records from last 5 minutes or after server start)
    """
    if request.method == 'POST':
        # Capture the raw text body from the ZKTeco device
        raw_data = request.get_data(as_text=True)
        
        if raw_data.strip():
            # Parse attendance data (tab-separated format)
            # Format: USERID \t TIMESTAMP \t STATUS \t VERIFY \t WORKCODE
            lines = raw_data.strip().split('\n')
            current_time = datetime.now()
            
            # Only show records from the last 5 minutes (real-time data)
            # This filters out old backlogged records the device might send
            time_threshold = current_time - timedelta(minutes=5)
            
            for line in lines:
                if not line.strip():
                    continue
                    
                parts = line.split('\t')
                
                if len(parts) >= 2:
                    user_id = parts[0].strip()
                    timestamp_str = parts[1].strip()
                    status = parts[2].strip() if len(parts) > 2 else '0'
                    
                    # Parse timestamp
                    try:
                        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                    except:
                        try:
                            timestamp = datetime.strptime(timestamp_str, '%Y/%m/%d %H:%M:%S')
                        except:
                            timestamp = current_time
                    
                    # FILTER: Only show records from the last 5 minutes (real-time)
                    # This prevents showing old backlogged data
                    if timestamp < time_threshold and timestamp < SERVER_START_TIME:
                        # Skip old records - don't display or upload
                        continue
                    
                    # Determine punch status
                    punch_status = '✅ CHECKED IN' if status == '0' else '✅ CHECKED OUT'
                    
                    # Simple, clean output - only for real-time data
                    time_display = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                    print(f"\n{punch_status} | User ID: {user_id} | Time: {time_display}")
                    
                    # Forward to backend if configured (silently)
                    environment = os.getenv('ADMS_DEFAULT_ENV', 'dev')
                    if environment == 'prod':
                        backend_url = os.getenv('PROD_BACKEND_URL', '')
                    else:
                        backend_url = os.getenv('DEV_BACKEND_URL', '')
                    
                    if backend_url:
                        upload_data = [{
                            'number': user_id,
                            'dateTime': timestamp.isoformat(),
                            'status': 'Check In' if status == '0' else 'Check Out',
                            'name': f"User {user_id}"
                        }]
                        
                        service_token = os.getenv('ADMS_SERVICE_TOKEN', '')
                        headers = {
                            'Content-Type': 'application/json',
                            'x-tenant': 'default'
                        }
                        
                        if service_token:
                            headers['Authorization'] = f'Bearer {service_token}'
                        
                        upload_url = f"{backend_url.rstrip('/')}/attendance/upload"
                        
                        try:
                            upload_response = requests.post(
                                upload_url,
                                json=upload_data,
                                headers=headers,
                                timeout=10
                            )
                            upload_response.raise_for_status()
                            print(f"   📤 Uploaded to backend successfully")
                        except Exception as e:
                            print(f"   ⚠️  Backend upload failed: {str(e)}")
        
        # Return "OK" to device to acknowledge receipt
        return "OK"
    
    # Initial setup sometimes sends a GET request
    return "OK"

@app.route('/adms/status', methods=['GET'])
def adms_status():
    """Health check endpoint for ADMS configuration"""
    return jsonify({
        'status': 'active',
        'endpoints': {
            'webhook': '/adms/webhook',
            'iclock_heartbeat': '/iclock/getrequest',
            'iclock_data': '/iclock/cdata'
        },
        'protocols': ['JSON Webhook', 'iClock Protocol'],
        'api_key_required': bool(os.getenv('ADMS_API_KEY', '')),
        'default_environment': os.getenv('ADMS_DEFAULT_ENV', 'dev')
    }), 200

@app.route('/network/ip', methods=['GET'])
def get_current_ip():
    """
    Get the current local IP address of this computer.
    Useful when switching networks - shows what IP to configure on the device.
    """
    try:
        # Connect to a remote server to determine local IP
        # This works even if you're behind NAT
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # Doesn't actually connect, just determines the local IP
            s.connect(('8.8.8.8', 80))
            local_ip = s.getsockname()[0]
        except Exception:
            local_ip = '127.0.0.1'
        finally:
            s.close()
        
        port = int(os.getenv('FLASK_PORT', '5000'))
        
        return jsonify({
            'local_ip': local_ip,
            'port': port,
            'server_url': f'http://{local_ip}:{port}',
            'iclock_heartbeat': f'http://{local_ip}:{port}/iclock/getrequest',
            'iclock_data': f'http://{local_ip}:{port}/iclock/cdata',
            'message': f'Configure your device Server Address to: {local_ip}',
            'note': 'This IP changes when you switch networks. Use ngrok for a permanent URL.'
        }), 200
    except Exception as e:
        return jsonify({
            'error': 'Failed to get IP address',
            'message': str(e)
        }), 500

@app.route('/exit', methods=['POST'])
@require_auth
def exit_app():
    import threading
    import time
    
    def delayed_exit():
        time.sleep(0.5)  # Small delay to allow browser to close
        os._exit(0)
    
    # Start delayed exit in a separate thread
    threading.Thread(target=delayed_exit, daemon=True).start()
    
    # Return success response to browser
    return jsonify({"status": "exiting"}), 200

def get_local_ip():
    """Get the local IP address of this computer"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 80))
            local_ip = s.getsockname()[0]
        except Exception:
            local_ip = '127.0.0.1'
        finally:
            s.close()
        return local_ip
    except Exception:
        return '127.0.0.1'

def start_flask():
    # Enable debug mode for development (auto-reload on code changes)
    # Set FLASK_ENV=development or FLASK_DEBUG=1 in .env to enable
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true' or os.getenv('FLASK_ENV') == 'development'
    port = int(os.getenv('FLASK_PORT', '5000'))
    
    # Bind to 0.0.0.0 to allow devices on network to connect (for iClock/ADMS)
    # Use '127.0.0.1' if you only want localhost access
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    
    if debug_mode:
        print("🚀 Flask running in DEVELOPMENT mode with auto-reload enabled")
        print("📝 Code changes will automatically restart the server")
    else:
        print("🚀 Flask running in PRODUCTION mode")
        print("💡 Set FLASK_DEBUG=True in .env to enable auto-reload")
    
    print(f"🌐 Server accessible at: http://{host}:{port}")
    if host == '0.0.0.0':
        local_ip = get_local_ip()
        print(f"   📍 Your local IP: {local_ip}")
        print(f"   🔗 Device Server Address: {local_ip}:{port}")
        print("   ✅ Devices on your network can connect to this server")
        print("   ⚠️  NOTE: This IP changes when you switch networks!")
        print("   💡 Use ngrok for a permanent URL (see NETWORK_SETUP.md)")
    
    print(f"\n✅ Server started at {SERVER_START_TIME.strftime('%Y-%m-%d %H:%M:%S')}")
    print("📋 Only showing real-time check-ins/outs (last 5 minutes)")
    print("   Old records will be filtered out automatically\n")
    
    app.run(debug=debug_mode, host=host, port=port, use_reloader=debug_mode)


def start_ngrok_tunnel(port):
    """Start ngrok tunnel to create a public URL"""
    try:
        from pyngrok import ngrok
        
        # Check if ngrok auth token is set
        ngrok_token = os.getenv('NGROK_AUTH_TOKEN', '')
        if ngrok_token:
            ngrok.set_auth_token(ngrok_token)
        
        # Start tunnel
        public_url = ngrok.connect(port)
        print(f"\n{'='*80}")
        print(f"🌍 NGROK TUNNEL ACTIVE")
        print(f"{'='*80}")
        print(f"🔗 Public URL: {public_url}")
        print(f"   📍 Heartbeat: {public_url}/iclock/getrequest")
        print(f"   📍 Data: {public_url}/iclock/cdata")
        print(f"\n💡 Configure your device Server Address to:")
        print(f"   {public_url.replace('https://', '').replace('http://', '')}")
        print(f"   (Remove http:// or https:// prefix)")
        print(f"\n✅ This URL works from ANY network!")
        print(f"{'='*80}\n")
        return public_url
    except ImportError:
        print("\n⚠️  pyngrok not installed. Install with: pip install pyngrok")
        print("   Or set ENABLE_NGROK=False in .env to disable this message\n")
        return None
    except Exception as e:
        print(f"\n⚠️  Failed to start ngrok: {str(e)}")
        print("   Continuing without ngrok tunnel...\n")
        return None

if __name__ == '__main__':
    # In development mode, run directly (allows auto-reload)
    # In production, use threading to keep browser open
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true' or os.getenv('FLASK_ENV') == 'development'
    
    # Check if we're in the reloader process (Flask sets WERKZEUG_RUN_MAIN when reloading)
    # Only open browser in the main process, not on reloads
    is_reloader = os.environ.get('WERKZEUG_RUN_MAIN') == 'true'
    
    port = int(os.getenv('FLASK_PORT', '5000'))
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    
    # Start ngrok tunnel if enabled (only in main process, not reloader)
    enable_ngrok = os.getenv('ENABLE_NGROK', 'False').lower() == 'true'
    ngrok_url = None
    if enable_ngrok and not is_reloader:
        ngrok_url = start_ngrok_tunnel(port)
    
    if debug_mode:
        # Development mode: run directly for auto-reload
        if not is_reloader:
            # Only open browser on first start, not on reload
            print("🔧 Development mode: Starting Flask with auto-reload...")
            print("🌐 Opening browser...")
            webbrowser.open("http://localhost:5000")
            print(f"\n✅ Server started at {SERVER_START_TIME.strftime('%Y-%m-%d %H:%M:%S')}")
            print("📋 Only showing real-time check-ins/outs (last 5 minutes)")
            print("   Old records will be filtered out automatically\n")
        else:
            # This is a reload, don't open new browser window
            print("🔄 Server reloaded (browser will refresh automatically)")
            # Update server start time on reload - use globals() to modify module-level variable
            import sys
            sys.modules[__name__].SERVER_START_TIME = datetime.now()
        
        print(f"🌐 Server accessible at: http://{host}:{port}")
        if host == '0.0.0.0':
            local_ip = get_local_ip()
            print(f"   📍 Your local IP: {local_ip}")
            print(f"   🔗 Device Server Address: {local_ip}:{port}")
            print("   ✅ Devices on your network can connect to this server")
            if not ngrok_url:
                print("   ⚠️  NOTE: This IP changes when you switch networks!")
                print("   💡 Set ENABLE_NGROK=True in .env for a permanent URL")
        
        app.run(debug=True, host=host, port=port, use_reloader=True)
    else:
        # Production mode: use threading
        threading.Thread(target=start_flask, daemon=True).start()
        print("🌐 Opening browser...")
        webbrowser.open("http://localhost:5000")
        # Keep the script running so the server stays alive
        import time
        while True:
            time.sleep(1)
