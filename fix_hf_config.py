#!/usr/bin/env python3
"""
Fix HuggingFace Space Configuration - Remove secrets, add as variables
"""

from huggingface_hub import HfApi
import sys

SPACE_ID = "agapemiteu/ManualAi"

print()
print("=" * 70)
print("🔧 Fixing ManualAI Space Configuration")
print("=" * 70)
print()

try:
    api = HfApi()
    user = api.whoami()
    print(f"✅ Logged in as: {user['name']}")
    print()
    
    # Step 1: Delete the secrets that are causing the collision
    print("🗑️  Removing secrets (to fix collision)...")
    secrets_to_remove = ["MANUAL_DISABLE_OCR", "MANUAL_INGESTION_TIMEOUT", "MANUALAI_LOG_LEVEL"]
    
    for secret_name in secrets_to_remove:
        try:
            print(f"   Removing {secret_name}...", end=" ")
            api.delete_space_secret(repo_id=SPACE_ID, key=secret_name)
            print("✅")
        except Exception as e:
            print(f"⚠️ ({e})")
    
    print()
    print("✅ Secrets removed!")
    print()
    print("=" * 70)
    print("📝 Manual Step Required")
    print("=" * 70)
    print()
    print("Unfortunately, the HuggingFace API doesn't support adding")
    print("regular VARIABLES programmatically (only secrets).")
    print()
    print("Please add these as VARIABLES (not secrets) manually:")
    print()
    print("1. Go to: https://huggingface.co/spaces/agapemiteu/ManualAi/settings")
    print()
    print("2. Scroll to 'Variables and secrets' section")
    print()
    print("3. Under 'Variables' (NOT 'Secrets'), add:")
    print()
    print("   Variable name: MANUAL_DISABLE_OCR")
    print("   Value: true")
    print("   (Click 'Add variable')")
    print()
    print("   Variable name: MANUAL_INGESTION_TIMEOUT")
    print("   Value: 120")
    print("   (Click 'Add variable')")
    print()
    print("   Variable name: MANUALAI_LOG_LEVEL")
    print("   Value: INFO")
    print("   (Click 'Add variable')")
    print()
    print("4. The space should automatically restart")
    print()
    print("5. Wait 2 minutes for rebuild")
    print()
    print("The difference:")
    print("  • SECRETS = Hidden values (for API keys, passwords)")
    print("  • VARIABLES = Public values (for configuration)")
    print()
    print("Use VARIABLES for these settings!")
    print()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
