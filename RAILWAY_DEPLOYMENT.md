# Railway Deployment Guide for Info Reeler 🚂

## Why Railway?
- ✅ **No size limits** - Perfect for OpenCV, ML libraries, and heavy dependencies
- ✅ **Built for AI/ML** - Designed for applications like yours
- ✅ **Easy deployment** - Simple GitHub integration
- ✅ **Free tier** - $5 credit monthly, perfect for development
- ✅ **Automatic HTTPS** - SSL certificates included
- ✅ **Environment variables** - Easy secret management

## Quick Deployment Steps

### 1. Create Railway Account
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub (recommended)
3. Connect your GitHub account

### 2. Deploy Your Project
1. **Click "New Project"**
2. **Select "Deploy from GitHub repo"**
3. **Choose your repository** (hack_vs)
4. **Railway will auto-detect** it's a Python project

### 3. Configure Environment Variables
1. Go to your project dashboard
2. Click on **"Variables"** tab
3. Add environment variable:
   - **Name**: `GEMINI_API_KEY`
   - **Value**: `AIzaSyDhkA938yD9Kv5EGi7opO710weUXK08okM`

### 4. Deploy
1. Railway will automatically:
   - Install dependencies from `requirements.txt`
   - Run `python3 run.py` (from Procfile)
   - Start your FastAPI server
2. **Wait 2-5 minutes** for deployment
3. **Get your URL** (e.g., `https://your-project.railway.app`)

## Configuration Files Created

### `railway.json`
- Configures Railway-specific settings
- Sets health check endpoint
- Configures restart policy

### `Procfile`
- Tells Railway how to start your app
- Uses `python3 run.py` command

## Post-Deployment

### 1. Test Your API
- Visit: `https://your-project.railway.app/health`
- Should return: `{"status": "healthy"}`

### 2. Update Chrome Extension
1. Edit `extension/config.js`
2. Change `API_URL` to your Railway URL:
   ```javascript
   API_URL: "https://your-project.railway.app"
   ```
3. Reload the extension in Chrome

### 3. Test Full Workflow
1. Go to any article
2. Click the Info Reeler extension
3. Generate a reel - should work perfectly!

## Railway vs Vercel

| Feature | Railway | Vercel |
|---------|---------|--------|
| Size Limit | ❌ None | ❌ 250MB |
| AI/ML Support | ✅ Excellent | ❌ Limited |
| Python Support | ✅ Full | ⚠️ Basic |
| Free Tier | ✅ $5/month | ✅ Generous |
| Setup Complexity | ✅ Easy | ⚠️ Complex |

## Troubleshooting

### Common Issues:
1. **Build fails**: Check that all dependencies are in `requirements.txt`
2. **Environment variables**: Make sure `GEMINI_API_KEY` is set
3. **Port issues**: Railway auto-assigns ports, your app should use `os.getenv('PORT', 8000)`

### Debug Steps:
1. Check Railway deployment logs
2. Test `/health` endpoint
3. Verify environment variables in dashboard
4. Check that all Python files are in correct locations

## Your Railway URL
Once deployed, your API will be available at:
`https://your-project-name.railway.app`

This will be much more reliable than Vercel for your AI/ML application! 🎉
