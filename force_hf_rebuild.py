#!/usr/bin/env python3
"""
Force HuggingFace Space to rebuild by making a dummy commit.
This triggers the Space to pull the latest code and rebuild the Docker container.
"""
import subprocess
import sys
from datetime import datetime

def force_rebuild():
    """Force HuggingFace Space rebuild by updating README timestamp."""
    
    print("🔄 Forcing HuggingFace Space rebuild...")
    print("=" * 60)
    
    # Update README with timestamp to trigger rebuild
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    readme_path = "hf-space/README.md"
    
    try:
        # Read current README
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            content = "# ManualAI - Car Manual RAG Chatbot\n\n"
        
        # Add/update timestamp line
        if "Last updated:" in content:
            # Update existing timestamp
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith("Last updated:"):
                    lines[i] = f"Last updated: {timestamp}"
                    break
            content = '\n'.join(lines)
        else:
            # Add timestamp at the end
            content += f"\n\nLast updated: {timestamp}\n"
        
        # Write updated README
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Updated {readme_path} with timestamp: {timestamp}")
        
        # Git add
        result = subprocess.run(
            ['git', 'add', readme_path],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"❌ Git add failed: {result.stderr}")
            return False
        
        # Git commit
        result = subprocess.run(
            ['git', 'commit', '-m', f'Force rebuild: Update timestamp {timestamp}'],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            if "nothing to commit" in result.stdout:
                print("⚠️  No changes detected, creating empty commit...")
                result = subprocess.run(
                    ['git', 'commit', '--allow-empty', '-m', f'Force rebuild: {timestamp}'],
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    print(f"❌ Empty commit failed: {result.stderr}")
                    return False
            else:
                print(f"❌ Git commit failed: {result.stderr}")
                return False
        
        print("✅ Committed changes")
        
        # Push to GitHub
        print("\n📤 Pushing to GitHub...")
        result = subprocess.run(
            ['git', 'push', 'origin', 'main'],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"❌ Push to GitHub failed: {result.stderr}")
            return False
        
        print("✅ Pushed to GitHub")
        
        # Push to HuggingFace using subtree
        print("\n📤 Pushing to HuggingFace Space (this triggers rebuild)...")
        result = subprocess.run(
            ['git', 'subtree', 'push', '--prefix', 'hf-space', 'hf', 'main'],
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode != 0:
            print(f"⚠️  Subtree push had issues: {result.stderr}")
            print(f"Output: {result.stdout}")
            # Try force push
            print("\n🔥 Trying force push to HuggingFace...")
            result = subprocess.run(
                ['git', 'push', 'hf', '`git subtree split --prefix hf-space main`:main', '--force'],
                capture_output=True,
                text=True,
                shell=True
            )
        
        print("✅ Pushed to HuggingFace")
        print("\n" + "=" * 60)
        print("✅ Force rebuild triggered!")
        print("\nThe Space will now:")
        print("1. Pull the latest code from git")
        print("2. Rebuild the Docker container")
        print("3. Restart with the new code")
        print("\nThis takes ~3-5 minutes. Check status at:")
        print("https://huggingface.co/spaces/Agapemiteu/ManualAi")
        print("\nWait 3 minutes, then test with:")
        print("  python test_upload.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = force_rebuild()
    sys.exit(0 if success else 1)
