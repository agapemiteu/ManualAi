# Render Deployment Guide for ManualAi

## Quick Deployment Steps

### 1. Sign Up / Sign In to Render

1. Go to **[render.com](https://render.com)**
2. Click **"Get Started"** or **"Sign In"**
3. **Sign in with GitHub**
4. Authorize Render to access your repositories

### 2. Create New Web Service

1. Click **"New +"** (top right)
2. Select **"Web Service"**
3. Find and **"Connect"** to `ManualAi` repository

### 3. Configure Service

**Basic Settings:**
- **Name**: `manualai-backend`
- **Region**: Choose closest to you
- **Branch**: `main`
- **Root Directory**: `api`
- **Runtime**: `Python 3`

**Build & Deploy:**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

**Plan:**
- Select **"Free"** ✅

**Environment Variables:**
- **Key**: `CORS_ALLOW_ORIGINS`
- **Value**: `https://manual-ai-psi.vercel.app` (or your Vercel URL)

### 4. Deploy

Click **"Create Web Service"** and wait 3-5 minutes for deployment.

Your backend URL will be: `https://manualai-backend.onrender.com`

### 5. Update Frontend (Vercel)

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your `manual-ai` project
3. **Settings** → **Environment Variables**
4. Edit `NEXT_PUBLIC_API_URL`:
   - Value: `https://manualai-backend.onrender.com`
5. **Deployments** → **Redeploy**

## Important Notes

### Free Tier Features:
- ✅ **Free forever** (no credit card required)
- ✅ **Automatic HTTPS**
- ✅ **Auto-deploys** from GitHub
- ✅ **750 hours/month** (enough for continuous operation)
- ⚠️ **Sleeps after 15 min inactivity** (wakes up in 30-50 seconds)

### Wake-Up Behavior:
The free tier sleeps after 15 minutes of inactivity. When someone visits:
1. First request takes 30-50 seconds (cold start)
2. Subsequent requests are instant
3. This is normal and expected for free tier

### Keeping Service Awake (Optional):
If you want to keep it always awake, you can:
- Upgrade to paid plan ($7/month)
- Use a ping service (like UptimeRobot) to keep it awake
- Accept the cold start (fine for portfolio/demo)

## Managing Your Deployment

### View Logs:
- Go to your service dashboard on Render
- Click **"Logs"** tab
- See real-time application logs

### Manual Deploy:
- Click **"Manual Deploy"** → **"Deploy latest commit"**

### Update Environment Variables:
- Go to **"Environment"** tab
- Add/edit variables
- Service will automatically redeploy

### Connect Custom Domain (Optional):
1. Go to **"Settings"** tab
2. Scroll to **"Custom Domain"**
3. Add your domain (e.g., `api.yourdomain.com`)
4. Follow DNS configuration instructions

## Monitoring

### Check Service Health:
Visit: `https://your-service.onrender.com/`

Should return: `{"message": "Welcome to ManualAi API!"}`

### Check Deployment Status:
- **Building**: Installing dependencies
- **Live**: Service is running
- **Deploy failed**: Check logs for errors

## Troubleshooting

### Deployment Fails:
1. Check **"Logs"** tab for errors
2. Verify `requirements.txt` is in `api/` folder
3. Check Python version compatibility

### Service Times Out:
- Increase timeout in Render dashboard (Settings → Advanced)
- Default is 60 seconds (usually sufficient)

### CORS Errors:
1. Verify `CORS_ALLOW_ORIGINS` environment variable
2. Include your Vercel URL without trailing slash
3. Redeploy service after changing

### Out of Memory:
- Free tier has 512 MB RAM
- Upgrade to paid plan if needed
- Or optimize ML model loading

## Cost Information

### Free Tier (Forever):
- **Cost**: $0
- **Hours**: 750/month
- **RAM**: 512 MB
- **Bandwidth**: 100 GB/month
- **Perfect for**: Portfolio projects, demos, learning

### Paid Plans (Optional):
- **Starter**: $7/month
  - No sleep
  - 1 GB RAM
  - Priority support
  
- **Standard**: $25/month
  - 2 GB RAM
  - More CPU
  - Better for production

## Portfolio Tips

### Add to Your Portfolio:
```markdown
**ManualAi** - AI-Powered Car Manual Assistant
- Tech Stack: Next.js, FastAPI, LangChain, ChromaDB
- Features: RAG-based Q&A, Document processing, Semantic search
- Live Demo: https://manual-ai-psi.vercel.app
- Backend: https://manualai-backend.onrender.com
- GitHub: https://github.com/agapemiteu/ManualAi
```

### Showcase Features:
- ✅ Full-stack deployment (Vercel + Render)
- ✅ CI/CD with GitHub integration
- ✅ RESTful API design
- ✅ Machine learning integration
- ✅ Modern UI/UX with Tailwind CSS

## Support

### Documentation:
- [Render Documentation](https://render.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

### Common Issues:
- [Render Community Forum](https://community.render.com/)
- [GitHub Issues](https://github.com/agapemiteu/ManualAi/issues)
