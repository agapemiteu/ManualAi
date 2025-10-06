# 🚀 Vercel Deployment Guide

## Step 1: Install Vercel CLI (if not already installed)

```powershell
npm install -g vercel
```

## Step 2: Login to Vercel

```powershell
vercel login
```

This will open a browser to authenticate.

## Step 3: Deploy to Vercel

From your project root:

```powershell
vercel
```

Follow the prompts:
- **Set up and deploy?** Yes
- **Which scope?** Your personal account
- **Link to existing project?** No (first time) / Yes (subsequent deploys)
- **Project name?** manualai (or your preferred name)
- **Directory?** ./ (current directory)
- **Override settings?** No

## Step 4: Set Environment Variable on Vercel

### Option A: Via Vercel CLI

```powershell
vercel env add NEXT_PUBLIC_API_URL production
```

When prompted, enter:
```
https://agapemiteu-manualai.hf.space
```

### Option B: Via Vercel Dashboard

1. Go to https://vercel.com/dashboard
2. Select your project
3. Go to **Settings** → **Environment Variables**
4. Add:
   - **Name:** `NEXT_PUBLIC_API_URL`
   - **Value:** `https://agapemiteu-manualai.hf.space`
   - **Environment:** Production, Preview, Development (all)
5. Click **Save**

## Step 5: Redeploy (if you added env var via dashboard)

```powershell
vercel --prod
```

## Step 6: Test Your Deployment

Your app will be deployed to a URL like:
- https://manualai-yourusername.vercel.app

Or your custom domain if configured.

### Test the connection:

1. Go to your Vercel URL
2. Try uploading a manual
3. Try chatting with the manual

---

## Quick Deploy Commands

### Development Preview
```powershell
vercel
```

### Production Deploy
```powershell
vercel --prod
```

### Deploy with Environment Variables
```powershell
# Set env var first
vercel env add NEXT_PUBLIC_API_URL production

# Then deploy
vercel --prod
```

---

## Troubleshooting

### CORS Issues

If you get CORS errors, you need to update your HuggingFace Space's CORS settings.

Check `hf-space/main.py` - it should have:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify your Vercel domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

This is already configured in your backend! ✅

### Environment Variable Not Working

If the API URL isn't being picked up:
1. Make sure it's named `NEXT_PUBLIC_API_URL` (must start with `NEXT_PUBLIC_`)
2. Redeploy after adding env vars
3. Clear browser cache

### Build Fails

Make sure all dependencies are in package.json:
```powershell
npm install
npm run build  # Test build locally
```

---

## Current Configuration

✅ **Backend:** https://agapemiteu-manualai.hf.space  
✅ **Status:** Running  
⏳ **Frontend:** Ready to deploy  

---

## Automatic Deployment (GitHub Integration)

For automatic deployments on git push:

1. Go to https://vercel.com/dashboard
2. Click **Add New** → **Project**
3. Import your GitHub repository
4. Vercel will auto-detect Next.js
5. Add environment variable:
   - `NEXT_PUBLIC_API_URL` = `https://agapemiteu-manualai.hf.space`
6. Deploy!

Every push to `main` will now auto-deploy to Vercel! 🚀

---

## Next Steps After Deployment

1. ✅ Deploy to Vercel
2. Test upload functionality
3. Test chat functionality
4. Share with users!
5. (Optional) Set up custom domain

---

**Ready to deploy? Run:** `vercel`
