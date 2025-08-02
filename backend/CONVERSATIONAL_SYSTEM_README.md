# Conversational Video System

This system creates conversational videos between **Narendra Modi** and **Donald Trump** discussing any topic. When each person speaks, their photo appears in the video.

## Features

- 🤖 **AI-Generated Scripts**: Natural conversational dialogue between Modi and Trump
- 🎤 **Multiple Voices**: Different voices for each speaker using ElevenLabs
- 📸 **Dynamic Photos**: Speaker photos appear when they're talking
- 🎬 **Vertical Video**: Optimized for social media (TikTok/Instagram Reels)
- ⏰ **Timeline Sync**: Perfect synchronization between audio and visual elements

## How It Works

1. **Script Generation**: AI creates natural dialogue between Modi and Trump
2. **Voice Generation**: Each speaker gets their own voice using ElevenLabs
3. **Timeline Creation**: System determines when each person speaks
4. **Video Creation**: Photos appear when each speaker is talking

## API Endpoints

### Generate Conversational Reel
```
POST /generate-conversational-reel
```

**Request Body:**
```json
{
  "url": "https://example.com/article",
  "text": "Your article content here",
  "title": "Optional title"
}
```

**Response:**
```json
{
  "script": "Generated conversational dialogue...",
  "audio_url": "/download/conversational_audio_20250802_123456.wav",
  "video_url": "/download/conversational_video_20250802_123456.mp4"
}
```

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables
Create a `.env` file with:
```
GEMINI_API_KEY=your_gemini_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
```

### 3. Configure Voice IDs
In `conversational_tts.py`, update the voice IDs:
```python
TRUMP_VOICE_ID = "your_trump_voice_id"
MODI_VOICE_ID = "your_modi_voice_id"
```

### 4. Run the Server
```bash
python main.py
```

## Testing the System

### Run the Test Script
```bash
python test_conversational_system.py
```

This will:
- Generate a conversational script about AI
- Create audio with alternating voices
- Generate video with speaker photos
- Save all files to `outputs/` directory

### Manual Testing
```bash
# Start the server
python main.py

# Test with curl
curl -X POST "http://localhost:8000/generate-conversational-reel" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Artificial Intelligence is transforming the world..."
  }'
```

## File Structure

```
backend/
├── conversational_tts.py      # Multi-speaker TTS system
├── conversational_video.py    # Video creation with speaker photos
├── llm.py                    # Script generation (updated)
├── main.py                   # API endpoints (updated)
├── test_conversational_system.py  # Test script
└── CONVERSATIONAL_SYSTEM_README.md
```

## Voice Configuration

### Getting Voice IDs from ElevenLabs

1. Go to [ElevenLabs Voice Library](https://elevenlabs.io/voice-library)
2. Find voices that sound like Modi and Trump
3. Copy the voice IDs and update in `conversational_tts.py`

### Example Voice IDs
```python
TRUMP_VOICE_ID = "ANHNqAseXGR3gBQps4vo"  # Current Trump voice
MODI_VOICE_ID = "pNInz6obpgDQGcFmaJgB"   # Replace with actual Modi voice
```

## Photo Configuration

### Default Photos
The system uses Wikipedia photos by default:
- **Modi**: Official portrait from Wikimedia Commons
- **Trump**: Official portrait from Wikimedia Commons

### Custom Photos
You can provide custom photo paths:
```python
# In conversational_video.py
MODI_PHOTO_URL = "path/to/modi_photo.jpg"
TRUMP_PHOTO_URL = "path/to/trump_photo.jpg"
```

## Script Format

The system generates **pure conversational dialogue** without annotations:

**Example Output:**
```
"Have you seen the latest developments in artificial intelligence? It's really changing everything."

"Yes, absolutely! The way companies are investing in AI is incredible. Billions of dollars going into research."

"And the impact on jobs is something we need to discuss seriously. Automation is reshaping entire industries."

"You're right about that. But we also need to focus on the opportunities AI creates for new types of work."
```

**No speaker labels, no annotations - just natural conversation!**

## Troubleshooting

### Common Issues

1. **Voice Generation Fails**
   - Check ElevenLabs API key
   - Verify voice IDs are correct
   - Check API quota limits

2. **Photo Download Fails**
   - System will create placeholder images
   - Check internet connection
   - Verify photo URLs are accessible

3. **Video Creation Fails**
   - Ensure all dependencies are installed
   - Check available disk space
   - Verify audio file exists

### Logs
Check `app.log` for detailed error messages and debugging information.

## Next Steps

1. **Add More Speakers**: Extend to support other political figures
2. **Custom Voices**: Allow users to upload custom voice samples
3. **Custom Photos**: Allow users to upload custom speaker photos
4. **Language Support**: Add support for multiple languages
5. **Video Effects**: Add transitions and visual effects

## Support

For issues or questions, check the logs in `app.log` or run the test script to verify system functionality. 