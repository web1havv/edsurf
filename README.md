# Info Reeler 🎬

Turn any article into a viral info reel with open-source AI! This project combines a Chrome extension with a Python backend to automatically generate engaging short-form videos from web articles.

## Features

- 📰 **Article Extraction**: Automatically extracts content from any webpage
- 🤖 **AI Script Generation**: Uses Gemini AI to create engaging scripts
- 🎨 **Image Generation**: Creates visuals for each scene using Gemini Vision
- 🔊 **Text-to-Speech**: Converts scripts to natural-sounding audio
- 🎬 **Video Assembly**: Combines images and audio into vertical videos
- 📱 **Chrome Extension**: Easy-to-use browser extension interface

## Quick Start

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
# Option 1: Use the setup script (recommended)
python setup_env.py

# Option 2: Manual setup
cp env_example.txt .env
# Edit .env and add your API keys:
# GEMINI_API_KEY=your_gemini_api_key_here
# OPENAI_API_KEY=your_openai_api_key_here (optional)

# Start the backend server
python start.py
```

### 2. Chrome Extension Setup

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" (top right)
3. Click "Load unpacked" and select the `extension/` folder
4. The Info Reeler extension should now appear in your toolbar

### 3. Usage

1. Navigate to any article you want to convert
2. Click the Info Reeler extension icon
3. Click "Generate Reel from This Page"
4. Wait for processing (this may take 1-2 minutes)
5. Download your generated audio and video files!

## API Keys Required

- **Gemini API Key** (Required): Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
- **OpenAI API Key** (Optional): For captions generation

## 🔒 Security Best Practices

### API Key Security
- **Never hardcode API keys** in your source code
- **Never commit API keys** to version control
- **Use environment variables** (`.env` file) to store keys
- **Rotate keys regularly** if they're compromised
- **Use the setup script** (`python setup_env.py`) for secure key entry

### If Your API Key is Exposed
1. **Immediately revoke the key** in your Google Cloud Console
2. **Generate a new key** to replace it
3. **Remove any hardcoded keys** from your code
4. **Check your git history** and remove any commits containing keys
5. **Update your `.env` file** with the new key

### Environment File Security
- The `.env` file is automatically ignored by git
- Keys are stored locally and never transmitted
- Use `getpass` for secure key input (implemented in setup script)

## Project Structure

```
info_reeler/
├── backend/                 # Python FastAPI server
│   ├── main.py             # Main API endpoints
│   ├── llm.py              # Gemini AI script generation
│   ├── image_gen.py        # Image generation
│   ├── tts.py              # Text-to-speech
│   ├── video.py            # Video assembly
│   └── utils.py            # Utility functions
├── extension/              # Chrome extension
│   ├── manifest.json       # Extension configuration
│   ├── popup.html          # Extension popup UI
│   ├── popup.js            # Popup functionality
│   ├── content.js          # Content extraction
│   └── background.js       # Background service worker
└── README.md              # This file
```

## API Endpoints

- `POST /generate-reel`: Generate a complete info reel
- `GET /download/{filename}`: Download generated files
- `GET /health`: Health check endpoint

## Troubleshooting

### Common Issues

1. **"GEMINI_API_KEY not found"**: Make sure you've created a `.env` file with your API key
2. **"TTS pipeline not available"**: The TTS model may take time to download on first run
3. **"Failed to generate images"**: Check your Gemini API quota and key validity
4. **Extension not working**: Make sure the backend is running on `http://localhost:8000`

### Performance Tips

- The first run may be slower as models download
- TTS and video generation are the most resource-intensive steps
- Consider using a GPU for faster processing

## Development

To contribute to this project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

If you encounter any issues, please:
1. Check the troubleshooting section above
2. Ensure all dependencies are installed
3. Verify your API keys are valid
4. Check the browser console for any JavaScript errors # hack_vs
