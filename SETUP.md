# Info Reeler Setup Guide 🚀

## Quick Start (Gemini-Only Implementation)

This implementation uses **only Gemini API** for all AI features - no external models needed!

### 1. Get Your Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key (starts with `AIza...`)

### 2. Backend Setup

```bash
cd backend

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (lightweight - no heavy ML models!)
pip install -r requirements.txt

# Set up your API key
echo "GEMINI_API_KEY=your_actual_api_key_here" > .env

# Start the server
python run.py
```

### 3. Chrome Extension Setup

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" (top right)
3. Click "Load unpacked" and select the `extension/` folder
4. The Info Reeler extension should now appear in your toolbar

### 4. Test Everything

```bash
# Test the API
python test_api.py
```

### 5. Usage

1. Navigate to any article
2. Click the Info Reeler extension icon
3. Click "Generate Reel from This Page"
4. Wait for processing (1-2 minutes)
5. Download your generated files!

## What's Included

✅ **Script Generation**: Uses Gemini to create engaging scripts  
✅ **Image Generation**: Creates placeholder images (can be enhanced with DALL-E/Stable Diffusion)  
✅ **Audio Generation**: Simple sine wave audio (can be enhanced with TTS services)  
✅ **Video Assembly**: Combines images and audio into vertical videos  
✅ **Chrome Extension**: Easy-to-use browser interface  

## API Endpoints

- `GET /health` - Health check
- `POST /generate-reel` - Generate complete info reel
- `GET /download/{filename}` - Download generated files

## Troubleshooting

### Common Issues

1. **"API key not valid"**: Make sure your Gemini API key is correct
2. **"uvicorn not found"**: Make sure you're in the virtual environment
3. **Extension not working**: Ensure backend is running on `http://localhost:8000`

### Performance Notes

- First run may be slower as models initialize
- Image generation creates simple colored rectangles (can be enhanced)
- Audio generation creates simple beep sounds (can be enhanced)

## Next Steps

To enhance the implementation:

1. **Better Images**: Integrate with DALL-E or Stable Diffusion
2. **Better Audio**: Integrate with ElevenLabs or Azure Speech
3. **Better Video**: Add captions and transitions
4. **Cloud Deployment**: Deploy to Heroku or AWS

## Files Structure

```
info_reeler/
├── backend/
│   ├── run.py              # Simple server startup
│   ├── main.py             # FastAPI endpoints
│   ├── llm.py              # Gemini script generation
│   ├── image_gen.py        # Image generation (placeholder)
│   ├── tts.py              # Simple audio generation
│   ├── video.py            # Video assembly
│   ├── test_api.py         # API testing
│   └── requirements.txt    # Lightweight dependencies
├── extension/              # Chrome extension
└── SETUP.md               # This file
```

## All Gemini Implementation! 🎉

This implementation uses **only Gemini API** for:
- ✅ Script generation
- ✅ Content analysis  
- ✅ Image prompts (creates placeholder images)
- ✅ No heavy ML models to download
- ✅ No external API dependencies
- ✅ Fast startup and deployment

Just add your Gemini API key and you're ready to go! 