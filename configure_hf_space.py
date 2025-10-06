#!/usr/bin/env python3
"""
HuggingFace Space Configuration Script
Automatically sets environment variables for ManualAI space
"""

from huggingface_hub import HfApi, login
import os
import sys
import time

def configure_space():
    """Configure HuggingFace Space environment variables"""
    
    # Configuration
    SPACE_ID = "agapemiteu/ManualAi"
    VARIABLES = {
        "MANUAL_DISABLE_OCR": "true",
        "MANUAL_INGESTION_TIMEOUT": "120",
        "MANUALAI_LOG_LEVEL": "INFO",
    }
    
    print("=" * 60)
    print("🚀 ManualAI HuggingFace Space Configuration")
    print("=" * 60)
    print()
    
    # Check if already logged in
    try:
        api = HfApi()
        # Try to get user info to check if logged in
        try:
            user = api.whoami()
            print(f"✅ Logged in as: {user['name']}")
            print()
        except Exception:
            print("⚠️  Not logged in to HuggingFace")
            print()
            print("Please log in first:")
            print("  1. Get your token from: https://huggingface.co/settings/tokens")
            print("  2. Run: huggingface-cli login")
            print("  OR")
            print("  3. Set HF_TOKEN environment variable")
            print()
            
            # Try to login
            token = input("Enter your HuggingFace token (or press Enter to skip): ").strip()
            if token:
                login(token=token)
                print("✅ Login successful!")
                print()
            else:
                print("❌ Cannot continue without authentication")
                return False
    except Exception as e:
        print(f"❌ Error checking authentication: {e}")
        return False
    
    # Set environment variables
    print(f"📝 Configuring space: {SPACE_ID}")
    print()
    
    for var_name, var_value in VARIABLES.items():
        try:
            print(f"  Setting {var_name} = {var_value}...", end=" ")
            
            # Add secret to space (API version compatible)
            api.add_space_secret(
                repo_id=SPACE_ID,
                key=var_name,
                value=var_value
            )
            
            print("✅")
            time.sleep(0.5)  # Rate limiting
            
        except Exception as e:
            print(f"❌")
            print(f"    Error: {e}")
            print(f"    Note: Variable might already exist or require manual setting")
    
    print()
    print("=" * 60)
    print("✅ Configuration Complete!")
    print("=" * 60)
    print()
    print("📋 Variables Set:")
    for var_name, var_value in VARIABLES.items():
        print(f"  • {var_name} = {var_value}")
    
    print()
    print("🔄 Next Steps:")
    print("  1. Go to: https://huggingface.co/spaces/agapemiteu/ManualAi/settings")
    print("  2. Verify the variables are listed under 'Variables and secrets'")
    print("  3. Click 'Factory Reboot' to restart the space")
    print("  4. Wait 2 minutes for rebuild")
    print("  5. Test upload at: https://manual-ai-psi.vercel.app/upload")
    print()
    print("⚡ Expected Results:")
    print("  • Processing time: 20-40 seconds")
    print("  • No timeout errors")
    print("  • Logs show 'OCR DISABLED'")
    print()
    
    return True

def verify_space():
    """Verify space is running"""
    import requests
    
    print("🔍 Verifying space status...")
    try:
        response = requests.get("https://agapemiteu-manualai.hf.space/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Space is {data.get('status', 'unknown')}")
            return True
        else:
            print(f"⚠️  Space returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"⚠️  Could not reach space: {e}")
        return False

if __name__ == "__main__":
    print()
    try:
        success = configure_space()
        print()
        verify_space()
        print()
        
        if success:
            print("🎉 All done! Check the space settings and restart it.")
            sys.exit(0)
        else:
            print("❌ Configuration incomplete. Please set variables manually.")
            print("   Instructions: See HUGGINGFACE-SETUP.md")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print()
        print("❌ Cancelled by user")
        sys.exit(1)
    except Exception as e:
        print()
        print(f"❌ Unexpected error: {e}")
        print()
        print("Please set variables manually:")
        print("  1. Go to: https://huggingface.co/spaces/agapemiteu/ManualAi/settings")
        print("  2. Add variables under 'Variables and secrets'")
        print("  3. See HUGGINGFACE-SETUP.md for details")
        sys.exit(1)
