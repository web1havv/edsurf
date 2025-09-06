# Vercel Deployment Guide for Info Reeler

## Prerequisites
- A Vercel account (sign up at https://vercel.com)
- Your project files ready for deployment

## Deployment Steps

### 1. Prepare Your Repository
Your project is now ready for deployment with the following files created:
- `vercel.json` - Vercel configuration
- `package.json` - Project metadata
- `requirements.txt` - Python dependencies
- `.vercelignore` - Files to exclude from deployment

### 2. Deploy via Vercel Web Interface

1. **Go to Vercel Dashboard**
   - Visit https://vercel.com/dashboard
   - Sign in to your account

2. **Import Project**
   - Click "New Project"
   - Choose "Import Git Repository"
   - Connect your GitHub/GitLab/Bitbucket account if not already connected
   - Select your repository

3. **Configure Project Settings**
   - **Framework Preset**: Select "Other" or "Python"
   - **Root Directory**: Leave as default (or set to project root)
   - **Build Command**: Leave empty (Vercel will auto-detect using vercel.json)
   - **Output Directory**: Leave empty
   - **Install Command**: Leave empty

4. **Set Environment Variables**
   - In the "Environment Variables" section, add:
     - `GEMINI_API_KEY`: Your Gemini API key (AIzaSyDhkA938yD9Kv5EGi7opO710weUXK08okM)

5. **Deploy**
   - Click "Deploy"
   - Wait for the deployment to complete (usually 2-5 minutes)

### 3. Alternative: Deploy via Vercel CLI (if you have Node.js)

If you have Node.js installed, you can use the CLI:

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy
vercel

# Set environment variables
vercel env add GEMINI_API_KEY
# Enter your API key when prompted

# Redeploy with environment variables
vercel --prod
```

### 4. Post-Deployment

After successful deployment:

1. **Test Your API**
   - Visit your Vercel URL (e.g., `https://your-project.vercel.app`)
   - Test the health endpoint: `https://your-project.vercel.app/health`
   - Test other endpoints as needed

2. **Update Chrome Extension**
   - Update the extension's `background.js` and `content.js` files
   - Change the API URL from `http://localhost:8000` to your Vercel URL
   - Reload the extension in Chrome

### 5. Important Notes

- **File Size Limits**: Vercel has limits on file sizes. Large assets (videos, fonts) are excluded via `.vercelignore`
- **Function Timeout**: Vercel has execution time limits. Long-running operations may need optimization
- **Environment Variables**: Keep your API keys secure and never commit them to git
- **CORS**: The app is configured to allow all origins for development. Consider restricting this for production

### 6. Troubleshooting

**Common Issues:**
- **Build Failures**: Check that all dependencies are in `requirements.txt`
- **Import Errors**: Ensure all Python files are in the correct directory structure
- **Environment Variables**: Verify they're set correctly in Vercel dashboard
- **CORS Issues**: Check that CORS middleware is properly configured

**Debug Steps:**
1. Check Vercel deployment logs
2. Test endpoints individually
3. Verify environment variables are set
4. Check file paths and imports

## Your Deployment URL
Once deployed, your API will be available at:
`https://your-project-name.vercel.app`

Update your Chrome extension to use this URL instead of localhost!

## Troubleshooting the dotenv Error

If you encounter the "ModuleNotFoundError: No module named 'dotenv'" error:

✅ **Fixed**: The project now uses `backend/vercel_entry.py` as the entry point, which:
- Doesn't rely on python-dotenv (uses Vercel's environment variables directly)
- Has proper error handling for missing API keys
- Is optimized for Vercel's serverless environment

The `vercel.json` configuration now points to the correct entry point and includes:
- Increased lambda size limit (50mb)
- Extended timeout (60 seconds)
- Proper environment variable handling
