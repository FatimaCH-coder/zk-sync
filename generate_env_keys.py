#!/usr/bin/env python3
"""
Helper script to generate ADMS configuration values for .env file
"""
import secrets
import sys

def generate_api_key():
    """Generate a secure random API key"""
    return secrets.token_urlsafe(32)

def main():
    print("=" * 80)
    print("ADMS Configuration Generator")
    print("=" * 80)
    print()
    
    # Generate API Key
    api_key = generate_api_key()
    print("1. ADMS_API_KEY (Generated for you):")
    print(f"   {api_key}")
    print()
    
    # Environment choice
    print("2. ADMS_DEFAULT_ENV:")
    print("   Choose: 'dev' or 'prod'")
    print("   - 'dev' = Development environment")
    print("   - 'prod' = Production environment")
    print()
    
    # Service token explanation
    print("3. ADMS_SERVICE_TOKEN:")
    print("   This is your backend authentication token.")
    print("   You can get it by:")
    print("   a) Logging into your HRMS backend and getting an access token")
    print("   b) Using a service account token from your backend admin")
    print("   c) Leaving it empty if your backend doesn't require authentication")
    print()
    print("   To get a token from login:")
    print("   1. Login to your HRMS system")
    print("   2. Open browser DevTools (F12)")
    print("   3. Go to Network tab")
    print("   4. Look for the login request")
    print("   5. Copy the 'access_token' or 'accessToken' from the response")
    print()
    
    # Generate .env content
    print("=" * 80)
    print("Copy this to your .env file:")
    print("=" * 80)
    print()
    print("# ADMS Configuration")
    print(f"ADMS_API_KEY={api_key}")
    print("ADMS_DEFAULT_ENV=dev  # Change to 'prod' for production")
    print("ADMS_SERVICE_TOKEN=your-backend-token-here  # Optional: get from backend login")
    print()
    print("=" * 80)
    
    # Option to write to file
    write_to_file = input("\nWould you like to append these to your .env file? (y/n): ").lower().strip()
    if write_to_file == 'y':
        env_content = f"\n# ADMS Configuration\nADMS_API_KEY={api_key}\nADMS_DEFAULT_ENV=dev\nADMS_SERVICE_TOKEN=\n"
        try:
            with open('.env', 'a') as f:
                f.write(env_content)
            print("\n✅ Successfully appended to .env file!")
            print("⚠️  Don't forget to:")
            print("   1. Set ADMS_DEFAULT_ENV to 'prod' if needed")
            print("   2. Add your ADMS_SERVICE_TOKEN (get from backend)")
        except FileNotFoundError:
            print("\n❌ .env file not found. Creating it...")
            with open('.env', 'w') as f:
                f.write(env_content)
            print("✅ Created .env file with ADMS configuration!")
        except Exception as e:
            print(f"\n❌ Error writing to .env: {e}")
            print("Please copy the values manually.")

if __name__ == '__main__':
    main()

