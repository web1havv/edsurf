# Render Deployment Guide for Info Reeler 🎨

## Why Render?
- ✅ **No size limits** - Handles heavy ML dependencies
- ✅ **Free tier** - 750 hours/month free
- ✅ **Easy setup** - Simple configuration
- ✅ **Auto-deploy** - GitHub integration
- ✅ **HTTPS included** - SSL certificates

## Quick Deployment Steps

### 1. Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Connect your repository

### 2. Create Web Service
1. **Click "New +"** → **"Web Service"**
2. **Connect your repository** (hack_vs)
3. **Configure service:**
   - **Name**: `info-reeler`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd backend && python3 run.py`
   - **Plan**: Free

### 3. Set Environment Variables
1. In the service dashboard, go to **"Environment"**
2. Add variable:
   - **Key**: `GEMINI_API_KEY`
   - **Value**: `AIzaSyDhkA938yD9Kv5EGi7opO710weUXK08okM`

### 4. Deploy
1. Click **"Create Web Service"**
2. Wait 5-10 minutes for deployment
3. Get your URL (e.g., `https://info-reeler.onrender.com`)

## Configuration Files

### `render.yaml`
- Defines service configuration
- Sets build and start commands
- Configures environment variables

## Post-Deployment

### 1. Test Your API
- Visit: `https://your-service.onrender.com/health`

### 2. Update Chrome Extension
- Change `API_URL` in `extension/config.js` to your Render URL

## Render vs Railway

| Feature | Render | Railway |
|---------|--------|---------|
| Free Tier | ✅ 750 hrs/month | ✅ $5 credit |
| Setup | ✅ Very Easy | ✅ Easy |
| Performance | ✅ Good | ✅ Excellent |
| AI/ML Support | ✅ Good | ✅ Excellent |

Both are great alternatives to Vercel for your project!
