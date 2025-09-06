# 🚀 Info Reeler - How to Use

## Quick Start

### 1. Start the Server
```bash
# Option 1: Use the startup script (recommended)
./start_server.sh

# Option 2: Manual start
cd backend
python3 main.py
```

### 2. Open Your Browser
Go to: **http://localhost:8000**

## Features

### 🎬 URL Reel Tab
- **Purpose**: Generate videos from article URLs
- **How to use**: 
  1. Paste an article URL
  2. Select speaker pair (Trump & Elon, Samay & Arpit, etc.)
  3. Click "Generate Video"
- **Output**: Video with speaker overlays and voiceover

### 📚 Case Study Tab
- **Purpose**: Analyze case studies and generate summaries
- **How to use**:
  1. Upload a PDF/DOCX file OR paste text
  2. Optionally select speaker pair (for script generation)
  3. Click "Generate Case Study Summary"
- **Output**: AI summary + optional conversational script + quiz

## Key Features

✅ **Working Features:**
- ✅ Case study file upload (PDF, DOCX, TXT)
- ✅ Case study text input
- ✅ AI-generated summaries
- ✅ Optional conversational scripts
- ✅ Interactive quizzes
- ✅ Multi-language support (12+ Indian languages)
- ✅ Translation functionality
- ✅ Video generation from URLs

## Troubleshooting

### Server Won't Start
```bash
# Make sure you're in the right directory
cd backend
python3 main.py
```

### Case Study Not Working
- Make sure you have text content (minimum 50 characters)
- Check browser console for errors (F12)
- Verify server is running on http://localhost:8000

### Video Generation Issues
- Ensure you have a valid article URL
- Check that the URL is accessible
- Video generation takes 2-5 minutes

## API Endpoints

- `GET /health` - Health check
- `POST /generate-case-study-text` - Generate case study from text
- `POST /generate-case-study` - Generate case study from file
- `POST /generate-reel` - Generate video from URL
- `POST /generate-quiz` - Generate quiz from content
- `POST /translate` - Translate text

## Support

If you encounter issues:
1. Check the server logs in the terminal
2. Verify all dependencies are installed
3. Make sure you're using Python 3
4. Check that the server is running on port 8000

---
**Status**: ✅ All systems working correctly!
