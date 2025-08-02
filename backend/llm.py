import google.generativeai as genai
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    logger.error("❌ GEMINI_API_KEY environment variable is not set!")
    raise ValueError("GEMINI_API_KEY environment variable is required. Please set it in your .env file or environment.")

logger.info(f"🔑 API Key loaded: {API_KEY[:10]}...{API_KEY[-4:] if len(API_KEY) > 14 else '***'}")

genai.configure(api_key=API_KEY)

def test_api_key():
    """
    Test the Gemini API key and return detailed status information
    """
    try:
        logger.info("🔑 Testing Gemini API key...")
        
        # Test with a simple prompt using gemini-1.5-flash
        model = genai.GenerativeModel('gemini-1.5-flash')
        test_prompt = "Hello, this is a test. Please respond with 'API key is working' if you can see this message."
        
        logger.info("🤖 Sending test request to Gemini API...")
        response = model.generate_content(test_prompt)
        
        if response and hasattr(response, 'text'):
            logger.info("✅ API key is valid and working!")
            logger.info(f"📝 Test response: {response.text}")
            
            return {
                "valid": True,
                "info": "API key is working correctly",
                "response": response.text,
                "model": "gemini-1.5-flash"
            }
        else:
            logger.error("❌ API key test failed - no valid response")
            return {
                "valid": False,
                "error": "No valid response from API",
                "response": str(response) if response else "No response"
            }
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"❌ API key test failed: {error_msg}")
        
        # Provide specific error information
        if "API_KEY_INVALID" in error_msg or "invalid" in error_msg.lower():
            return {
                "valid": False,
                "error": "Invalid API key",
                "details": error_msg
            }
        elif "quota" in error_msg.lower():
            return {
                "valid": True,
                "error": "API quota exceeded",
                "details": error_msg
            }
        elif "network" in error_msg.lower() or "connection" in error_msg.lower():
            return {
                "valid": False,
                "error": "Network connection issue",
                "details": error_msg
            }
        elif "404" in error_msg and "models" in error_msg:
            return {
                "valid": True,
                "error": "Model not available for this API key",
                "details": error_msg
            }
        else:
            return {
                "valid": False,
                "error": "Unknown API error",
                "details": error_msg
            }

SCRIPT_PROMPT = """
Create a clean, engaging 60-90 second info reel script from this article.
Style: Viral social media, hook-driven, punchy delivery
Structure: Hook → 3-4 key points → Call-to-action
Tone: Conversational, energetic, informative but accessible
Target: Short-form vertical video (TikTok/Instagram Reels)

CRITICAL REQUIREMENTS:
- Generate ONLY the speech text that will be spoken
- NO scene markers like [SCENE 1] or [HOOK]
- NO formatting like **Voiceover** or **(description)**
- NO parenthetical descriptions
- NO visual descriptions
- Just pure, clean speech text that flows naturally
- Keep it conversational and engaging
- Make it sound like someone speaking naturally

Article: {article_text}

Generate ONLY clean speech text:
"""

def generate_script(article_text: str) -> str:
    try:
        logger.info(f"🤖 Generating script for article of length: {len(article_text)} characters")
        prompt = SCRIPT_PROMPT.format(article_text=article_text)
        
        logger.info("🤖 Sending request to Gemini API...")
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        result = response.text.strip() if hasattr(response, 'text') else str(response)
        logger.info(f"✅ Script generated successfully, length: {len(result)} characters")
        logger.debug(f"📜 Script preview: {result[:200]}...")
        
        return result
    except Exception as e:
        logger.error(f"❌ Failed to generate script: {str(e)}")
        raise Exception(f"Failed to generate script: {str(e)}") 

CONVERSATIONAL_SCRIPT_PROMPT = """
Create a HILARIOUS, realistic 60-90 second conversational script between Elon Musk and Donald Trump discussing this article.

CRITICAL REQUIREMENTS:
- Create ONLY natural dialogue between Elon and Trump
- NO annotations, scene markers, or formatting
- NO speaker labels like "Elon:" or "Trump:"
- NO asterisks, parentheses, or special formatting
- NO stage directions like (scoffs), (laughs), etc.
- Just pure conversational dialogue that flows naturally
- Make it EXTREMELY FUNNY and capture their real-world feud/dynamics
- Include their actual speaking styles, mannerisms, and famous phrases
- Reference their real conflicts, Twitter feuds, and public disagreements
- Make it sound like two people having a real, heated but funny conversation
- Each speaker should have distinct personality and speaking style
- Keep it engaging, informative, and HILARIOUS
- Target length: 60-90 seconds when spoken
- Make it suitable for social media (TikTok/Instagram Reels)

CRITICAL FOCUS REQUIREMENT:
- STAY FOCUSED ON THE ACTUAL ARTICLE CONTENT
- Discuss the specific topics, facts, and details from the article
- Don't get distracted by unrelated topics or personal feuds
- Make the conversation ABOUT the article content, not about their personal relationship
- Reference specific points, data, or claims from the article
- Keep the humor and personality but centered on the article topic
- EXPLAIN THE CONCEPT IN DEPTH while being funny
- Make complex topics accessible and entertaining

CONVERSATION STRUCTURE:
- Create ONLY 6-8 total segments (3-4 exchanges)
- Each speaker should have 3-4 substantial speaking turns
- Make each response longer and more detailed
- Natural back-and-forth conversation about the article
- Include reactions, questions, and responses about the article content
- End with a natural conclusion about the article topic

REAL-WORLD DYNAMICS TO CAPTURE:
- Elon's tech-savvy, sometimes awkward but confident style
- Trump's bombastic, "bigly" speaking style
- Their Twitter feuds and public disagreements
- Elon's SpaceX/Tesla achievements vs Trump's political style
- Their different approaches to AI, technology, and business
- Include their actual catchphrases and mannerisms

SEGMENT LENGTH:
- Each speaking turn should be 10-15 seconds when spoken
- Make responses substantial but concise
- Keep total duration to 60-90 seconds maximum
- Aim for 6-8 total segments (3-4 exchanges)

HUMOR REQUIREMENTS:
- Make it EXTREMELY FUNNY with real-world nuances
- Include mild cuss words and casual language
- Capture their actual speaking patterns and mannerisms
- Use their famous catchphrases and expressions
- Include references to their real conflicts and feuds
- Make it sound like two people actually arguing/fighting
- Include sarcasm, insults, and playful jabs
- Reference their Twitter beefs and public disagreements
- BUT keep the focus on the article content, not personal drama

EXPLANATION REQUIREMENTS:
- Break down complex concepts in simple terms
- Use analogies and real-world examples
- Make technical topics accessible to everyone
- Explain the "why" and "how" behind concepts
- Connect concepts to real-world applications
- Make it educational AND entertaining

FORMATTING RULES:
- Use only normal punctuation: periods, commas, question marks
- NO asterisks, parentheses, brackets, or special characters
- NO stage directions or descriptions
- NO emphasis markers or formatting
- Just clean, natural speech

Article: {article_text}

Generate ONLY clean, natural conversational dialogue with 6-8 short segments:
"""

def generate_conversational_script(article_text: str) -> str:
    try:
        logger.info(f"🤖 Generating conversational script for article of length: {len(article_text)} characters")
        prompt = CONVERSATIONAL_SCRIPT_PROMPT.format(article_text=article_text)
        
        logger.info("🤖 Sending conversational script request to Gemini API...")
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        result = response.text.strip() if hasattr(response, 'text') else str(response)
        logger.info(f"✅ Conversational script generated successfully, length: {len(result)} characters")
        logger.debug(f"📜 Script preview: {result[:200]}...")
        
        return result
    except Exception as e:
        logger.error(f"❌ Failed to generate conversational script: {str(e)}")
        raise Exception(f"Failed to generate conversational script: {str(e)}") 