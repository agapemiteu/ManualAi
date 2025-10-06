#!/usr/bin/env python3
"""
Startup script to ensure all required directories exist with proper permissions.
This runs BEFORE the main FastAPI app to avoid any Docker permission issues.
"""
import os
import sys
from pathlib import Path

def ensure_directories():
    """Create all required directories with proper permissions."""
    
    # List of all directories we need
    required_dirs = [
        "/tmp/manualai/uploads",
        "/tmp/manualai/manual_store",
        "/tmp/manualai/nltk_data",
        "/tmp/manualai/hf_cache",
        "/tmp/ocr_cache",
        "/tmp/matplotlib",
    ]
    
    print("🚀 ManualAI Startup Check...")
    print("=" * 50)
    
    for dir_path in required_dirs:
        path = Path(dir_path)
        try:
            # Create directory if it doesn't exist
            path.mkdir(parents=True, exist_ok=True)
            
            # Try to create a test file to verify write permissions
            test_file = path / ".write_test"
            test_file.touch()
            test_file.unlink()
            
            print(f"✅ {dir_path}")
        except PermissionError as e:
            print(f"❌ {dir_path} - Permission denied: {e}")
            print(f"   Attempting to use alternative location...")
            
            # Fallback to home directory if /tmp fails
            home_dir = Path.home() / ".manualai" / Path(dir_path).name
            try:
                home_dir.mkdir(parents=True, exist_ok=True)
                test_file = home_dir / ".write_test"
                test_file.touch()
                test_file.unlink()
                print(f"✅ Using fallback: {home_dir}")
                
                # Update environment variable to point to fallback
                env_var_map = {
                    "uploads": "MANUALAI_UPLOAD_DIR",
                    "manual_store": "MANUALAI_STORAGE_DIR",
                    "nltk_data": "NLTK_DATA",
                    "hf_cache": "HF_HOME",
                    "ocr_cache": "MANUALAI_OCR_CACHE",
                    "matplotlib": "MPLCONFIGDIR",
                }
                
                dir_name = Path(dir_path).name
                if dir_name in env_var_map:
                    os.environ[env_var_map[dir_name]] = str(home_dir)
                    
            except Exception as fallback_error:
                print(f"❌ Fallback also failed: {fallback_error}")
                print(f"   This may cause issues during runtime!")
        except Exception as e:
            print(f"⚠️  {dir_path} - Unexpected error: {e}")
    
    print("=" * 50)
    print("✅ Startup checks complete!")
    print()
    
    # Verify Python version
    print(f"🐍 Python: {sys.version}")
    print(f"📁 Working Directory: {Path.cwd()}")
    print(f"👤 User: {os.getenv('USER', os.getenv('USERNAME', 'unknown'))}")
    print()

if __name__ == "__main__":
    ensure_directories()
