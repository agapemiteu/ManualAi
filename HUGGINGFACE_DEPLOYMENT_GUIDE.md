# HuggingFace Spaces Deployment Guide

## 🚀 Quick Deploy to HuggingFace Spaces

### Prerequisites

1. **HuggingFace Account**
   - Sign up at [huggingface.co](https://huggingface.co)
   - Create access token at [Settings > Access Tokens](https://huggingface.co/settings/tokens)

2. **Git LFS** (for large files)
   ```bash
   # Install Git LFS
   git lfs install
   ```

---

## 📋 Step-by-Step Deployment

### Step 1: Create New Space

1. Go to [huggingface.co/new-space](https://huggingface.co/new-space)
2. Fill in details:
   - **Space name:** `ManualAi` (or your choice)
   - **License:** MIT
   - **SDK:** Gradio
   - **Space hardware:** CPU Basic (free tier)
   - **Visibility:** Public

3. Click **Create Space**

### Step 2: Prepare Files

From your local repository, you need these files in the Space:

```
ManualAi/ (HF Space)
├── app.py                    # Gradio interface
├── rag_chain.py              # Production RAG system  
├── document_loader.py        # PDF processing
├── requirements.txt          # Python dependencies
├── README.md                 # Space description
└── data/
    └── 2023-Toyota-4runner-Manual.pdf  # The manual (if < 50MB)
```

### Step 3: Clone Your Space Locally

```bash
# Clone the empty space
git clone https://huggingface.co/spaces/YOUR_USERNAME/ManualAi
cd ManualAi

# Configure Git LFS for large files
git lfs track "*.pdf"
git add .gitattributes
```

### Step 4: Copy Files

```bash
# Copy application files
cp ../car-manual-rag-chatbot/hf-space/app.py .
cp ../car-manual-rag-chatbot/hf-space/rag_chain.py .
cp ../car-manual-rag-chatbot/hf-space/document_loader.py .

# Copy requirements
cp ../car-manual-rag-chatbot/hf-space/requirements_hf.txt requirements.txt

# Copy README
cp ../car-manual-rag-chatbot/hf-space/README_HF.md README.md

# Copy PDF (if smaller than 50MB)
mkdir data
cp ../car-manual-rag-chatbot/data/2023-Toyota-4runner-Manual.pdf data/
```

### Step 5: Commit and Push

```bash
# Add all files
git add .

# Commit
git commit -m "Initial deployment of ManualAi RAG system"

# Push to HuggingFace
git push
```

### Step 6: Wait for Build

1. Go to your space: `https://huggingface.co/spaces/YOUR_USERNAME/ManualAi`
2. Wait for build to complete (~5-10 minutes)
3. Once built, your app will be live!

---

## ⚙️ Configuration Options

### Environment Variables

If you need to set environment variables (like HF_TOKEN for private models):

1. Go to your Space settings
2. Click on "Variables and secrets"
3. Add: `HF_TOKEN` = your token

### Hardware Upgrade

If the free CPU is too slow:

1. Go to Space settings
2. Select "Hardware"
3. Upgrade to CPU Upgrade ($0.03/hour) or GPU

---

## 🐛 Troubleshooting

### Build Fails

**Check logs:**
- Click on "Logs" tab in your Space
- Look for Python errors or missing dependencies

**Common issues:**
```bash
# Missing dependency
# Solution: Add to requirements.txt

# PDF too large (>50MB for free tier)
# Solution: Use Git LFS or upgrade to paid tier

# Import errors
# Solution: Check all imports in app.py and rag_chain.py
```

### App Runs But Errors on Query

**Check:**
1. PDF file is in correct location (`data/2023-Toyota-4runner-Manual.pdf`)
2. All model downloads completed
3. Enough disk space for vector store

### Slow Performance

**Options:**
1. Upgrade hardware (paid)
2. Reduce INITIAL_TOP_K from 60 to 30
3. Use smaller embedding model
4. Enable caching

---

## 📊 Monitoring

### Check App Status

Visit: `https://huggingface.co/spaces/YOUR_USERNAME/ManualAi`

### View Logs

Click "Logs" tab to see:
- Build process
- Model loading
- User queries
- Errors

### Analytics

HF Spaces provides:
- View count
- Like count
- User engagement

---

## 🔄 Updates

To update your deployed app:

```bash
# Make changes locally
cd ManualAi

# Edit files
nano app.py

# Commit and push
git add .
git commit -m "Update: improved UI"
git push

# HF will automatically rebuild
```

---

## 🎯 After Deployment

### Update README.md

Add live demo badge:

```markdown
[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-HuggingFace-yellow)](https://huggingface.co/spaces/YOUR_USERNAME/ManualAi)
```

### Share It!

- Add to your resume
- Share on LinkedIn
- Tweet about it
- Add to GitHub README

### Example Posts

**LinkedIn:**
```
🚀 Just deployed my RAG system to HuggingFace Spaces!

ManualAi is an intelligent car manual Q&A system that achieves 64% accuracy (±2 pages) on a 608-page manual - an 800% improvement over keyword baseline!

Features:
✅ Hybrid semantic + keyword search
✅ Cross-encoder reranking
✅ Production-ready architecture
✅ Beautiful Gradio interface

Try it live: [your-space-url]
Code: [your-github-url]

#MachineLearning #RAG #NLP #AI #DataScience
```

**Twitter:**
```
🚗 Built & deployed ManualAi - an intelligent car manual Q&A system!

📊 64% accuracy (±2 pages)
🚀 800% improvement over baseline
🔬 11 experiments, systematic optimization
💻 Live demo on @huggingface Spaces

Try it: [link]
Code: [link]

#MachineLearning #RAG #AI
```

---

## 📁 Final Checklist

Before going live:

- [ ] All files copied to Space
- [ ] requirements.txt has all dependencies
- [ ] PDF is accessible (or using external URL)
- [ ] README.md is informative
- [ ] app.py launches without errors
- [ ] Tested with example questions
- [ ] Added live demo link to GitHub README
- [ ] Shared on social media

---

## 🎉 Success!

Your RAG system is now live and accessible to anyone!

**Next steps:**
1. Monitor usage and feedback
2. Iterate based on user questions
3. Add to portfolio/resume
4. Use in job applications

---

## 💡 Tips for Interviews

When discussing this project:

1. **Start with results:** "64% accuracy, 800% improvement"
2. **Explain architecture:** Hybrid search, reranking, voting
3. **Show experiments:** "Tested 11 configurations systematically"
4. **Discuss challenges:** Over-optimization, plateau effect
5. **Demo live:** Show the HF Space!

---

## 📞 Support

If you encounter issues:

1. Check [HF Spaces Documentation](https://huggingface.co/docs/hub/spaces)
2. Visit [HF Community Forums](https://discuss.huggingface.co/)
3. Open issue on GitHub repo

---

**Good luck with your deployment! 🚀**
