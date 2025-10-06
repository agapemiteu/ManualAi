# 🚀 Deploy to Vercel via GitHub (Automatic Deployments)

## The Easy Way - GitHub Integration ✨

Vercel can automatically deploy your app from GitHub. Every push to your repository will trigger a new deployment!

---

## Step 1: Push Your Code to GitHub

Your code is already on GitHub at:
- **Repo:** https://github.com/agapemiteu/ManualAi

Make sure your latest changes are pushed:
```powershell
git add .
git commit -m "Ready for Vercel deployment"
git push origin main
```

✅ **Already done!** Your repo is up to date.

---

## Step 2: Connect GitHub to Vercel

### Go to Vercel Dashboard
1. Visit: https://vercel.com
2. Click **"Sign Up"** or **"Login"** (use GitHub account for easiest setup)
3. Authorize Vercel to access your GitHub account

### Import Your Repository
1. Click **"Add New"** → **"Project"**
2. Select **"Import Git Repository"**
3. Find **"agapemiteu/ManualAi"** in the list
4. Click **"Import"**

---

## Step 3: Configure Your Project

Vercel will auto-detect Next.js settings. You just need to:

### Set Environment Variable
In the **"Configure Project"** screen:

1. Expand **"Environment Variables"**
2. Add:
   - **Name:** `NEXT_PUBLIC_API_URL`
   - **Value:** `https://agapemiteu-manualai.hf.space`
   - **Environments:** Check all (Production, Preview, Development)

3. Click **"Deploy"**

---

## Step 4: Wait for Deployment

Vercel will:
- ✅ Clone your repository
- ✅ Install dependencies (`npm install`)
- ✅ Build your app (`npm run build`)
- ✅ Deploy to a live URL

**Takes:** ~2-3 minutes

---

## Step 5: Your App is Live! 🎉

You'll get a URL like:
- **Production:** `https://manual-ai-yourusername.vercel.app`
- **Custom Domain:** (optional) Configure in settings

### Test It:
1. Visit your Vercel URL
2. Go to the Upload page
3. Try uploading a manual
4. Chat with your manual!

---

## 🔄 Automatic Deployments (The Magic!)

Now, **every time you push to GitHub**, Vercel will automatically:

1. **Detect the push** (via webhook)
2. **Build your app** with latest code
3. **Deploy** to production
4. **Send you a notification**

### Try it:
```powershell
# Make a change
echo "# Updated" >> README.md

# Commit and push
git add README.md
git commit -m "Test auto-deploy"
git push origin main

# Watch Vercel dashboard - new deployment starts automatically! 🚀
```

---

## 🌿 Branch Previews (Bonus!)

Every branch and PR gets its own preview URL:

```powershell
# Create a feature branch
git checkout -b feature/new-ui

# Make changes and push
git push origin feature/new-ui

# Vercel creates a preview URL automatically!
# https://manual-ai-git-feature-new-ui-yourusername.vercel.app
```

Perfect for testing before merging to main!

---

## 📊 Vercel Dashboard Features

Access at: https://vercel.com/dashboard

- **Deployments:** See all deployments and their status
- **Analytics:** View traffic and performance
- **Logs:** Debug issues in production
- **Domains:** Add custom domains
- **Environment Variables:** Update API URLs
- **Preview Deployments:** Test PRs before merging

---

## 🔧 Update Environment Variables Later

If you need to change the API URL:

1. Go to https://vercel.com/dashboard
2. Select your project
3. Go to **Settings** → **Environment Variables**
4. Edit `NEXT_PUBLIC_API_URL`
5. **Redeploy** (Vercel will prompt you)

---

## ✅ Current Setup

- ✅ **Backend:** https://agapemiteu-manualai.hf.space (HuggingFace)
- ✅ **CORS:** Enabled for all origins
- ✅ **Frontend Code:** Ready in GitHub
- ✅ **Environment Variable:** `NEXT_PUBLIC_API_URL` configured locally
- ⏳ **Vercel Deployment:** Ready to deploy!

---

## 🎯 Quick Setup Checklist

1. ✅ Backend deployed and working
2. ✅ CORS enabled for Vercel
3. ✅ Code pushed to GitHub
4. ⏳ Go to https://vercel.com
5. ⏳ Import repository
6. ⏳ Add `NEXT_PUBLIC_API_URL` env var
7. ⏳ Deploy!

---

## 🐛 Troubleshooting

### Build Fails
- Check build logs in Vercel dashboard
- Test build locally: `npm run build`
- Verify all dependencies are in `package.json`

### API Not Connecting
- Check environment variable name: `NEXT_PUBLIC_API_URL` (must have `NEXT_PUBLIC_` prefix)
- Verify backend URL: https://agapemiteu-manualai.hf.space
- Check browser console for CORS errors

### Environment Variable Not Working
- Must start with `NEXT_PUBLIC_` for client-side access
- Redeploy after adding/changing env vars
- Clear browser cache

---

## 🎊 Benefits of GitHub Integration

✅ **Automatic deployments** on every push  
✅ **Preview deployments** for every PR  
✅ **Rollback** to any previous deployment  
✅ **No manual uploads** - just push code  
✅ **Team collaboration** - multiple developers  
✅ **CI/CD built-in** - no extra setup  

---

## 📚 Next Steps After Deployment

1. ✅ Deploy to Vercel
2. Test upload functionality
3. Test chat functionality  
4. (Optional) Add custom domain
5. Share with users!
6. Monitor analytics
7. Iterate and improve!

---

## 🔗 Useful Links

- **Vercel Dashboard:** https://vercel.com/dashboard
- **Your Backend:** https://agapemiteu-manualai.hf.space
- **Your GitHub Repo:** https://github.com/agapemiteu/ManualAi
- **Vercel Docs:** https://vercel.com/docs

---

# Ready to Deploy?

1. Go to https://vercel.com
2. Login with GitHub
3. Import `agapemiteu/ManualAi`
4. Add `NEXT_PUBLIC_API_URL` env var
5. Click Deploy!

**That's it!** Your car manual chatbot will be live in minutes! 🚀✨
