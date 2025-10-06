# 🔄 FORCE REBUILD INSTRUCTIONS

## The Issue:
Your code is pushed to HuggingFace, but the Space is still running the OLD Docker container.

## ✅ Solution: Force a Rebuild

### Option 1: Manual Restart (Recommended) - 2 minutes
1. Go to: **https://huggingface.co/spaces/Agapemiteu/ManualAi/settings**
2. Scroll down to "Factory Reboot"
3. Click **"Factory Reboot"** button
4. Wait 2-3 minutes for rebuild
5. Test again with: `python test_upload.py`

### Option 2: Make a Dummy Commit - 5 minutes
```powershell
# Add a comment to trigger rebuild
echo "# Force rebuild" >> hf-space/README.md
git add hf-space/README.md
git commit -m "chore: Force rebuild"
git push origin main
git subtree push --prefix hf-space hf main
```
Then wait 3-4 minutes for automatic rebuild.

### Option 3: Use HuggingFace CLI (if you have token)
```powershell
# Install CLI
pip install huggingface-hub

# Login with your token
huggingface-cli login

# Restart Space
python restart_hf_space.py
```

---

## How to Know When It's Ready:

Watch the logs at: https://huggingface.co/spaces/Agapemiteu/ManualAi

Look for:
```
🚀 ManualAI Startup Check...
==================================================
✅ /tmp/manualai/uploads
OR
❌ /tmp/manualai/uploads - Permission denied
✅ Using fallback: /app/.manualai/uploads
```

If you see `/app/.manualai` instead of `/.manualai`, it's working!

---

## Why This Happened:

HuggingFace Spaces caches Docker containers. When you push code:
1. ✅ Code updates on GitHub/HF repo
2. ❌ Docker container doesn't automatically rebuild
3. ❌ Old code keeps running until manual restart

**Fix:** Always do "Factory Reboot" after pushing critical changes!

---

## Test After Reboot:

```powershell
# Wait for rebuild (2-3 minutes)
Start-Sleep -Seconds 180

# Test upload
python test_upload.py
```

Look for:
- ✅ Status: 202 (upload accepted)
- ✅ Manual ready!
- ✅ RAG chain working!

---

**Go to Settings and click Factory Reboot now!** 🚀
