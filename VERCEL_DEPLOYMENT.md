# 🚀 Vercel Deployment Guide for ManualAi

## Quick Deploy

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/agapemiteu/ManualAi)

## What Gets Deployed

This Vercel deployment includes:
- ✅ **Next.js Frontend** - Modern, responsive UI
- ✅ **API Route** - Proxies requests to HuggingFace Space
- ✅ **Edge Functions** - Fast, global response times

**Backend:** The ML inference runs on HuggingFace Spaces (already deployed!)

## Architecture

```
User → Vercel (Next.js + API) → HuggingFace Space (RAG Backend)
```

## Manual Deployment Steps

### 1. Prerequisites
- GitHub account with ManualAi repository
- Vercel account (free tier works!)

### 2. Deploy to Vercel

**Option A: Using Vercel CLI**
```bash
npm install -g vercel
vercel
```

**Option B: Using Vercel Dashboard**
1. Go to https://vercel.com/new
2. Import your GitHub repository
3. Configure project:
   - **Framework Preset**: Next.js
   - **Root Directory**: `./`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

### 3. Environment Variables (Optional)

No environment variables needed! The app connects directly to your public HuggingFace Space.

### 4. Deployment

Click "Deploy" and wait 2-3 minutes. Your app will be live at:
```
https://manual-ai-[your-username].vercel.app
```

## Local Development

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Open http://localhost:3000
```

## Features

- 🎨 Modern, responsive UI
- ⚡ Edge-optimized API routes
- 🔗 Integrates with HuggingFace backend
- 📱 Mobile-friendly design
- 🎯 Example questions for easy testing

## Custom Domain (Optional)

1. Go to your Vercel project settings
2. Navigate to **Domains**
3. Add your custom domain
4. Follow DNS configuration instructions

## Troubleshooting

### API Not Working
- Check that HuggingFace Space is running
- Verify the Space URL in `app/api/chat/route.ts`

### Build Failures
```bash
# Clear cache and rebuild
npm run clean
npm install
npm run build
```

### Slow Response Times
- HuggingFace cold starts take 15-30 seconds
- First request after inactivity may be slow
- Subsequent requests are fast (~2-3 seconds)

## Performance

- **Initial Load**: <1s (Vercel Edge)
- **API Response**: 2-20s (depends on HF cold start)
- **Global CDN**: Yes (Vercel's global network)

## Cost

- **Vercel**: FREE (Hobby tier)
- **HuggingFace**: FREE (Community tier)
- **Total**: $0/month 💰

## Links

- 🌐 **Live Demo**: https://[your-vercel-url].vercel.app
- 🤗 **HuggingFace**: https://huggingface.co/spaces/Agapemiteu/ManualAi
- 📊 **Portfolio**: https://agapemiteu.github.io/ManualAi
- 💻 **GitHub**: https://github.com/agapemiteu/ManualAi

## Support

Questions? Open an issue on GitHub!
