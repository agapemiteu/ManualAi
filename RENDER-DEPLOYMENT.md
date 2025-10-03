# Render Deployment Guide

## Backend Deployment (Python FastAPI)

### 1. Setup

1. Sign in to [Render](https://render.com) with GitHub
2. Click **"New +"** → **"Web Service"**
3. Connect to `ManualAi` repository

### 2. Configuration

```
Name:           manualai-backend
Region:         Closest to you
Branch:         main
Root Directory: api
Runtime:        Python 3
Build Command:  pip install -r requirements.txt
Start Command:  uvicorn main:app --host 0.0.0.0 --port $PORT
Plan:           Free
```

**Environment Variable:**
```
CORS_ALLOW_ORIGINS = https://manual-ai-psi.vercel.app
```

### 3. Deploy

Click **"Create Web Service"** → Wait 3-5 minutes

Backend URL: `https://manualai-backend.onrender.com`

### 4. Update Frontend

1. [Vercel Dashboard](https://vercel.com/dashboard) → Project Settings
2. **Environment Variables** → Edit `NEXT_PUBLIC_API_URL`
3. Value: `https://manualai-backend.onrender.com`
4. **Redeploy**

## Free Tier Info

- ✅ Free forever (no credit card)
- ✅ 750 hours/month (continuous operation)
- ✅ Auto-deploys from GitHub
- ⚠️ Sleeps after 15 min inactivity (30-50s wake time)

## Troubleshooting

**Deployment fails**: Check logs for errors  
**CORS errors**: Verify `CORS_ALLOW_ORIGINS` environment variable  
**Timeout**: Service sleeps after inactivity (expected on free tier)

## Resources

- [Render Docs](https://render.com/docs)
- [GitHub Issues](https://github.com/agapemiteu/ManualAi/issues)
