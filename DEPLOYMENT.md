# ManualAi Deployment Guide

## 🚀 Deploy to Production

### Recommended: Vercel (Frontend) + Render (Backend)

This is the best setup for portfolio projects - both are **free forever**!

#### Frontend (Vercel)

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit - ManualAi"
   git branch -M main
   git remote add origin https://github.com/yourusername/manualai.git
   git push -u origin main
   ```

2. **Deploy on Vercel:**
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your GitHub repository
   - Framework Preset: **Next.js**
   - Root Directory: `./` (leave default)
   - Build Command: `npm run build`
   - Output Directory: `.next`
   
3. **Environment Variables:**
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
   ```
   *(Update after backend deployment)*

4. **Deploy!** - Click deploy

#### Backend (Render)

1. **Go to [render.com](https://render.com)**
2. Sign in with GitHub
3. Click "New +" → "Web Service"
4. Connect to `ManualAi` repository
5. **Configure:**
   - Name: `manualai-backend`
   - Root Directory: `api`
   - Runtime: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Plan: **Free** ✅
   
6. **Environment Variables:**
   ```
   CORS_ALLOW_ORIGINS=https://your-vercel-app.vercel.app
   ```

7. **Deploy!** - Takes 3-5 minutes (installing ML models)

Your backend URL: `https://manualai-backend.onrender.com`

6. **Deploy!** - Railway will auto-deploy

7. **Get Your URL** - Copy the railway.app URL

8. **Update Vercel** - Go back to Vercel and update `NEXT_PUBLIC_API_URL`

---

### Option 2: Deploy Backend to Render

1. **Go to [render.com](https://render.com)**
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. **Settings:**
   - Name: `manualai-api`
   - Root Directory: `api`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Instance Type: Free or Starter

5. **Environment Variables:**
   ```
   PYTHON_VERSION=3.10.0
   CORS_ALLOW_ORIGINS=https://your-vercel-app.vercel.app
   ```

6. **Deploy!**

---

### Option 3: Deploy Everything to Vercel (Monorepo)

1. **Install Vercel CLI:**
   ```bash
   npm i -g vercel
   ```

2. **Login:**
   ```bash
   vercel login
   ```

3. **Deploy:**
   ```bash
   vercel
   ```

4. **Configure:**
   - Framework: Next.js
   - Add API routes as serverless functions

---

### Option 4: Docker Deployment

#### Build and Run Locally

```bash
# Backend
cd api
docker build -t manualai-backend .
docker run -p 8000:8000 manualai-backend

# Frontend
cd ..
docker build -t manualai-frontend .
docker run -p 3000:3000 manualai-frontend
```

#### Deploy to Any Cloud Provider

- **AWS ECS**
- **Google Cloud Run**
- **Azure Container Instances**
- **DigitalOcean App Platform**

---

## 📝 Post-Deployment Checklist

- [ ] Frontend is live and accessible
- [ ] Backend API is responding
- [ ] CORS is configured correctly
- [ ] Environment variables are set
- [ ] Can upload a test manual
- [ ] Can chat with the uploaded manual
- [ ] Error tracking is setup (Optional: Sentry)
- [ ] Analytics is setup (Optional: Google Analytics)
- [ ] Custom domain configured (Optional)

---

## 🔧 Production Configuration

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=https://your-backend-url.com
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX  # Optional
```

### Backend (.env.local)
```bash
CORS_ALLOW_ORIGINS=https://your-frontend-url.com,https://www.your-domain.com
DEFAULT_MANUAL_BRAND=default
MANUAL_PATH=../data/default-manual.html
MANUAL_UPLOAD_DIR=../data/uploads
MANUAL_STORAGE_DIR=../data/manual_store
```

---

## 🔐 Security Recommendations

1. **Enable HTTPS** - Both Vercel and Railway provide this by default
2. **Configure CORS** - Only allow your frontend domain
3. **Rate Limiting** - Add rate limiting to your API
4. **File Upload Limits** - Already set to 50MB
5. **API Keys** - If using external services, store in environment variables
6. **Content Security Policy** - Configure in next.config.js

---

## 📊 Monitoring & Analytics

### Frontend
- Vercel Analytics (built-in)
- Google Analytics
- Sentry for error tracking

### Backend
- Railway/Render logs
- Sentry for Python
- Custom logging with CloudWatch/Datadog

---

## 🆘 Troubleshooting

### Frontend not connecting to Backend
- Check `NEXT_PUBLIC_API_URL` environment variable
- Verify CORS settings in backend
- Check browser console for errors

### Backend 500 errors
- Check railway/render logs
- Verify all Python dependencies are installed
- Check file upload permissions

### Vector store issues
- Ensure storage directory is writable
- Check disk space on backend server

---

## 💰 Cost Estimates

### Free Tier (For Testing)
- **Vercel**: Free (Hobby plan)
- **Railway**: Free credits ($5/month)
- **Total**: ~$0/month (with free credits)

### Production (Low Traffic)
- **Vercel**: Free - $20/month
- **Railway**: $5-20/month
- **Total**: ~$5-40/month

### Production (High Traffic)
- **Vercel Pro**: $20/month
- **Railway Pro**: $20-100/month
- **Total**: ~$40-120/month

---

## 🎉 You're Done!

Your ManualAi is now live! Share it with the world:

🌐 **Live Site**: `https://your-app.vercel.app`

📢 **Share on:**
- Twitter
- Reddit (r/webdev, r/cars)
- Product Hunt
- Hacker News

---

**Need Help?** Open an issue on GitHub or contact us!
