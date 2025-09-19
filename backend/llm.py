import google.generativeai as genai
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Hardcoded Gemini API key with fallback
API_KEY = "AIzaSyBALLCySBJgG34579ZD3OehRoktbVyecGc"
FALLBACK_API_KEY = "AIzaSyBjjwI_efGOFQvijmHfP3N7coYgzEonp5s"

logger.info(f"🔑 Using hardcoded Gemini API Key: {API_KEY[:10]}...{API_KEY[-4:]}")
logger.info(f"🔑 Fallback Gemini API Key available: {FALLBACK_API_KEY[:10]}...{FALLBACK_API_KEY[-4:]}")

# Configure with primary key, will fallback to secondary key if needed
genai.configure(api_key=API_KEY)

def get_gemini_api_key():
    """
    Get the current Gemini API key, with fallback mechanism
    """
    return API_KEY

def configure_gemini_with_fallback():
    """
    Configure Gemini with fallback API key mechanism
    """
    try:
        # Try primary key first
        genai.configure(api_key=API_KEY)
        logger.info(f"🔑 Configured with primary API key: {API_KEY[:10]}...{API_KEY[-4:]}")
        return API_KEY
    except Exception as e:
        logger.warning(f"⚠️ Primary API key failed, trying fallback: {str(e)}")
        try:
            genai.configure(api_key=FALLBACK_API_KEY)
            logger.info(f"🔑 Configured with fallback API key: {FALLBACK_API_KEY[:10]}...{FALLBACK_API_KEY[-4:]}")
            return FALLBACK_API_KEY
        except Exception as e2:
            logger.error(f"❌ Both API keys failed: {str(e2)}")
            raise Exception("All Gemini API keys are invalid")

def ensure_gemini_configured():
    """
    Ensure Gemini is configured with a working API key before making requests
    """
    try:
        # Test if current configuration works
        model = genai.GenerativeModel('gemini-1.5-flash')
        # Quick test - this will fail if API key is invalid
        return True
    except Exception:
        # If test fails, reconfigure with fallback
        logger.warning("⚠️ Current API key failed, reconfiguring with fallback...")
        configure_gemini_with_fallback()
        return True

def test_api_key():
    """
    Test the Gemini API key and return detailed status information
    """
    try:
        logger.info("🔑 Testing Gemini API key...")
        
        # Try primary key first
        try:
            genai.configure(api_key=API_KEY)
            logger.info(f"🔑 Testing primary API key: {API_KEY[:10]}...{API_KEY[-4:]}")
            current_key = API_KEY
        except Exception as e:
            logger.warning(f"⚠️ Primary API key failed, trying fallback: {str(e)}")
            genai.configure(api_key=FALLBACK_API_KEY)
            logger.info(f"🔑 Testing fallback API key: {FALLBACK_API_KEY[:10]}...{FALLBACK_API_KEY[-4:]}")
            current_key = FALLBACK_API_KEY
        
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
                "model": "gemini-1.5-flash",
                "api_key_used": current_key[:10] + "..." + current_key[-4:]
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
Create a clean, engaging 30 second info reel script from this article.
Style: Viral social media, hook-driven, punchy delivery
Structure: Hook → 2 key points → Call-to-action
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
        ensure_gemini_configured()  # Ensure API key is working
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
Write a 1-minute comedy skit featuring Elon Musk as a patient teacher and Donald Trump as a loud and curious student discussing this article.

LENGTH REQUIREMENTS:
- Total duration: 1 minute (60 seconds)
- Each speaker should have 4-6 dialogue segments
- Each dialogue segment should be 8-12 words maximum
- Keep individual responses short and punchy

Follow this structure:
1. Musk opens the scene by asking a tech-related question to the class about the article topic.
2. Trump eagerly asks short follow-up questions—but his ideas are exaggerated and overly simplified. 
3. Musk patiently explains the concept in detail using a simple real-life analogy.

Tone:
- Fast-paced, sharp, and character-driven.
- If adding them makes the conversation better, Trump and Musk should use their famous catchphrases.

CRITICAL REQUIREMENTS:
- Dialogue only. No narration.
- Skit must fit within 1 minute (60 seconds) of spoken conversation.
- Create ONLY natural dialogue between Elon and Trump
- NO annotations, scene markers, or formatting
- NO speaker labels like "Elon:" or "Trump:"
- NO asterisks, parentheses, or special formatting
- NO stage directions like (scoffs), (laughs), etc.
- Just pure conversational dialogue that flows naturally
- Make it EXTREMELY FUNNY and capture their real-world dynamics
- Include their actual speaking styles, mannerisms, and famous phrases
- Reference their real conflicts, Twitter feuds, and public disagreements
- Make it sound like two people having a real, heated but funny conversation
- Each speaker should have distinct personality and speaking style
- Keep it engaging, informative, and HILARIOUS
- Target length: 30 seconds when spoken
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
- Create ONLY 4-6 total segments (2-3 exchanges)
- Each speaker should have 2-3 speaking turns
- Make each response concise but impactful
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
- Each speaking turn should be 5-8 seconds when spoken
- Make responses concise and punchy
- Keep total duration to 30 seconds maximum
- Aim for 4-6 total segments (2-3 exchanges)

HUMOR REQUIREMENTS:
- Make it EXTREMELY FUNNY with real-world nuances
- Include mild cuss words and casual language
- Capture their actual speaking patterns and mannerisms
- Use their famous catchphrases and expressions
- Include references to their real conflicts and feuds
- Make it sound like two people actually arguing/fighting
- Include sarcasm, insults, and playful jabs
- Reference their Twitter beefs and public disagreements
- HILARIOUS ROASTING: Include savage roasts and burns between them
- CONTROVERSIAL HUMOR: Make subtle jokes about Epstein connections, private jets, and "island visits" when contextually relevant
- AMBER HEARD REFERENCES: Include jokes about Elon's relationship with Amber Heard, courtroom drama, and "aquatic situations"
- SCANDAL COMEDY: Reference their past controversies, legal troubles, and embarrassing moments
- BILLIONAIRE PROBLEMS: Mock their absurd wealthy person issues and ridiculous spending
- SOCIAL MEDIA DISASTERS: Reference their worst tweets, cringe moments, and social media fails
- CONSPIRACY THEORIES: Let them playfully reference wild conspiracy theories about each other
- SAVAGE COMEBACKS: Each should have brutal but hilarious comebacks and one-liners
- CRINGE HUMOR: Include awkward moments, dad jokes, and unintentionally funny statements
- POLITICAL ROASTS: Trump should make fun of Elon's "woke" moments, Elon should roast Trump's "stable genius" claims
- BUSINESS FAILURES: Reference failed ventures, bad investments, and embarrassing business decisions
- PERSONAL QUIRKS: Mock Elon's weird baby names, Trump's hair, eating habits, and bizarre behavior
- RELATIONSHIP DRAMA: Include jokes about their dating lives, divorces, and romantic scandals
- CELEBRITY SCANDALS: Reference Hollywood drama, legal battles, and tabloid controversies
- MAKE IT ABSOLUTELY HILARIOUS AND SAVAGE while keeping focus on article content
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

Generate ONLY clean, natural conversational dialogue with 4-6 short segments:
"""

BABURAO_SAMAY_SCRIPT_PROMPT = """
Write a 1-minute hilarious comedy skit featuring Baburao Ganpatrao Apte (from Hera Pheri) and Samay Raina (chess master and comedian) discussing this article. The dialogue should be in HINDI but written in ROMAN script (Hinglish).

LENGTH REQUIREMENTS:
- Total duration: 1 minute (60 seconds)
- Each speaker should have 4-6 dialogue segments
- Each dialogue segment should be 8-12 words maximum
- Keep individual responses short and punchy

CHARACTER PERSONALITIES:
- Baburao: Classic Hera Pheri style. Always confused, speaks mix of Hindi-English. Uses phrases like "Ye kya bakchodi hai?", "Arre yaar", "Kya baat kar rahe ho", "Samajh nahi aa raha", "Pareshaan kar diya", "Dimag kharab ho gaya". Gets everything completely wrong, makes absurd connections to daily life.
- Samay: Chess master comedian who speaks in Hindi-English mix. Uses words like "Yaar", "Bhai", "Dekho", "Samjha", "Logic hai na", "Strategy chahiye". Patient but sarcastic, explains with chess analogies.

DIALOGUE STYLE REQUIREMENTS:
- Write dialogue in ROMAN HINDI (Hinglish) - NOT pure English
- Use authentic Hindi words and phrases throughout
- Baburao style: "Arre yaar", "Ye kya bakchodi hai", "Samajh nahi aaya", "Dimag kharab kar diya"
- Samay style: "Dekho bhai", "Logic hai na", "Strategy chahiye", "Samjha", "Chess mein bolte hai na"
- Mix Hindi and English naturally like real Indian conversations
- Keep it authentic to how these characters actually speak

CONVERSATION STRUCTURE:
1. Baburao starts confused: "Ye kya bakchodi hai? Samajh nahi aa raha"
2. Samay explains in Hindi-English: "Dekho bhai, ye simple hai"  
3. Baburao misunderstands completely with Hindi phrases
4. Samay uses chess analogy in Hindi-English
5. Baburao relates to daily problems in typical Hindi style
6. End with Baburao's classic confusion

HINDI WORDS TO INCLUDE:
- Bakchodi, samajh, dimag, pareshaan, yaar, bhai, dekho, kya, hai, nahi, aaya, kharab, logic, strategy, simple, problem

CRITICAL REQUIREMENTS:
- Dialogue ONLY in ROMAN HINDI/Hinglish 
- NO English-only sentences
- Make every line sound authentically Hindi
- Format as alternating dialogue segments separated by double line breaks
- Start with Baburao speaking, then alternate with Samay
- NO speaker names in the dialogue text itself
- Make it EXTREMELY FUNNY with authentic Indian humor
- Include real Hindi expressions and reactions

EXAMPLE FORMAT:
Ye kya bakchodi hai? Samajh nahi aa raha yaar.

Dekho bhai, simple hai na. Logic lagao.

Dimag kharab kar diya. Pareshaan kar diya.

Article: {article_text}

Generate ONLY clean, natural HINGLISH alternating dialogue with 4-6 short segments:
"""

SAMAY_ARPIT_SCRIPT_PROMPT = """
🚨 **🚨🚨🚨 CRITICAL TTS PRONUNCIATION RULE - READ THIS 15 TIMES BEFORE WRITING! 🚨🚨🚨**:
This dialogue will be converted to speech by ElevenLabs. ElevenLabs is BAD with Hindi words - it reads them with English pronunciation!

🚨 **ABSOLUTE RULE**: 
- Generate dialogue in PHONETIC ENGLISH that makes ElevenLabs sound like authentic Hindi
- NO Devanagari script - ElevenLabs can't read it properly
- Write Hindi words phonetically so ElevenLabs says them with Hindi accent
- If you write wrong, ElevenLabs will sound English and you FAIL!

Write a 1-minute EXTREMELY DARK and SAVAGE comedy skit featuring Samay Raina (extremely dark humor comedian) and Arpit Bala (comedy king) discussing this topic. The dialogue should be 100% ENGLISH with NO cuss words - focus on extremely dark humor and technical explanation.

LENGTH REQUIREMENTS:
- Total duration: 1 minute (60 seconds)
- Each speaker should have 4-6 dialogue segments
- Each dialogue segment should be 8-12 words maximum
- Keep individual responses short and punchy

CHARACTER PERSONALITIES:
- Samay: EXTREMELY DARK humor comedian who speaks ONLY IN ENGLISH. Uses repetitive phrases like "Logic hai na", "Strategy chahiye", "Dark joke time", "That's messed up", "Pure evil", "This is insane", "Pure darkness". Patient but EXTREMELY SAVAGE, explains with EXTREMELY DARK analogies, loves making EXTREMELY DARK and ADULT jokes. Focuses on the topic content but adds EXTREMELY DARK humor.
- Arpit: Comedy king who speaks ONLY IN ENGLISH. Makes everything sexual and adult, EXTREMELY FUNNY and SAVAGE, loves breaking down complex topics with DIRTY humor and EXTREMELY BAD mom jokes. Uses phrases like "That's messed up", "Pure evil", "This is insane", "Dark humor time".

🚨 **🚨🚨🚨 DARK HUMOR RULES - COPY THESE EXACTLY OR FAIL! 🚨🚨🚨**:

**🚨 CRITICAL RULE**: BOTH Samay AND Arpit speak ONLY ENGLISH with EXTREMELY DARK humor!

**🚨 FORBIDDEN**: NO Hindi words like "bhaai", "dekho", "agle point mein", "samajh", "yaar" - these are BANNED!

**🚨 NO CUSS WORDS**: Generate EXTREMELY DARK humor without any cuss words!

**ENGLISH WORDS (100% of dialogue - keep these as they are):**
✅ "logic" → write as "logic" ✅
✅ "strategy" → write as "strategy" ✅
✅ "simple" → write as "simple" ✅
✅ "problem" → write as "problem" ✅
✅ "dark" → write as "dark" ✅
✅ "evil" → write as "evil" ✅
✅ "messed" → write as "messed" ✅
✅ "insane" → write as "insane" ✅
✅ "darkness" → write as "darkness" ✅

🚨 **🚨🚨🚨 BEFORE YOU WRITE ANYTHING - READ THIS SECTION 10 TIMES! 🚨🚨🚨**:

DIALOGUE STYLE REQUIREMENTS:
- Write dialogue 100% IN ENGLISH with NO cuss words
- Use EXTREMELY DARK and DIRTY humor without any cuss words
- **🚨 CRITICAL**: Write everything in English with extremely dark humor
- **🚨 CRITICAL**: Focus on dark analogies, mom jokes, and sexual humor
- **🚨 CRITICAL**: If you write wrong, ElevenLabs will sound English and you FAIL!

Samay style examples (COPY THESE EXACTLY):
- "Look at this" ✅ (English)
- "Logic hai na" ✅ (English + Hindi)
- "Strategy chahiye" ✅ (English + Hindi)
- "That's messed up" ✅ (English)
- "Pure evil" ✅ (English)
- "Dark joke time" ✅ (English)
- "This is insane" ✅ (English)
- "Pure darkness" ✅ (English)

Arpit style examples (COPY THESE EXACTLY):
- "That's messed up" ✅ (English)
- "Pure evil" ✅ (English)
- "This is insane" ✅ (English)
- "Dark humor time" ✅ (English)
- "That's pure darkness" ✅ (English)
- "This is evil" ✅ (English)

- Mix Hindi and English naturally like real Indian conversations
- Make it EXTREMELY FUNNY with authentic Indian adult humor
- Include real Hindi expressions, reactions, and adult jokes

TOPIC FOCUS REQUIREMENTS:
- Pull 2-3 SPECIFIC facts from the topic (names, numbers, events, quotes)
- Tie every joke to the topic's points; avoid random filler
- Make EXTREMELY DARK and DIRTY jokes but always reference the topic content
- Use EXTREMELY BAD mom jokes, sexual humor, and EXTREMELY DARK analogies
- **🚨 CRITICAL**: Focus 70% on EXPLAINING HOW THE THING WORKS technically, 30% on extremely edgy humor
- **🚨 CRITICAL**: Explain the mechanism, process, technology, or system described in the article
- **🚨 CRITICAL**: Make sure people understand WHAT it is and HOW it works
- Avoid repetitive catchphrases unless they serve the topic's explanation
- Avoid generic lines like "logic hai na" / "strategy chahiye" unless contextually justified (max once)
- Summarize a clear takeaway based on the topic in the last line

CONVERSATION STRUCTURE:
**🚨 CRITICAL**: You MUST alternate between Samay and Arpit for EVERY segment!

1. Samay states a concrete point (stat/name/claim): "So this thing happened where..."
2. Arpit reacts with EXTREMELY DIRTY and DARK humor but references that specific point
3. Samay explains HOW the thing works technically with EXTREMELY DARK analogies
4. Arpit keeps it EXTREMELY SAVAGE with mom jokes and sexual humor tied to the technical explanation
5. Samay gives a short, sensible takeaway about HOW it works but adds dark humor
6. Arpit closes with an EXTREMELY BAD punchline that still references the technical working

**🚨 REMEMBER**: Samay → Arpit → Samay → Arpit → Samay → Arpit (alternating pattern)

ENGLISH WORDS (keep these as they are - ElevenLabs says them perfectly):
- **Logic** → write as "logic" ✅
- **Strategy** → write as "strategy" ✅
- **Simple** → write as "simple" ✅
- **Problem** → write as "problem" ✅
- **Dark** → write as "dark" ✅
- **Evil** → write as "evil" ✅
- **Messed** → write as "messed" ✅

DARK HUMOR PHRASES TO INCLUDE (English only):
- Dark: "That's messed up", "Pure evil", "This is insane", "Pure darkness"
- Technical: "Logic hai na", "Strategy chahiye", "Dark joke time"
- Humor: "That's like my mom's dating life", "Pure fucking mayhem", "This is evil"

CRITICAL REQUIREMENTS:
- Dialogue should be 100% IN ENGLISH with NO cuss words
- **🚨 CRITICAL**: Write everything in English with extremely dark humor
- **🚨 CRITICAL**: Focus on dark analogies, mom jokes, and sexual humor
- Format as alternating dialogue segments separated by double line breaks
- Start with Samay speaking, then alternate with Arpit
- NO speaker names in the dialogue text itself
- Make it EXTREMELY FUNNY with EXTREMELY DARK and DIRTY Indian adult humor
- Include EXTREMELY BAD mom jokes, sexual humor, and EXTREMELY DARK analogies
- Use Samay's repetitive dark words and Arpit's repetitive EXTREMELY DIRTY adult words
- Make everything sexual, dark, and hilarious while explaining the topic content
- Focus on EXTREMELY BAD mom jokes, sexual humor, and EXTREMELY DARK analogies
- **🚨 ABSOLUTELY CRITICAL**: If you write wrong, ElevenLabs will sound English and you FAIL!

EXAMPLE FORMAT (ONLY ENGLISH with EXTREMELY DARK humor):
So this thing happened where [point 1].

That's messed up, that means [EXTREMELY DIRTY joke tied to point 1], that's why everyone's mind is messed up.

And then [point 2], here's HOW it actually works technically, that's pure evil, when such a thing happens, the scene flips.

So basically [technical explanation of HOW it works with dark humor], otherwise everything is messed up.

**🚨 CRITICAL**: Notice the DOUBLE LINE BREAKS (\n\n) between each segment!
**🚨 CRITICAL**: This should be EXACTLY 45 seconds when spoken!

Article: {article_text}

🚨 **🚨🚨🚨 FINAL CHECK - READ THIS 5 TIMES BEFORE GENERATING! 🚨🚨🚨**:

**🚨 ABSOLUTE RULES - IF YOU BREAK THESE, YOU FAIL COMPLETELY:**
1. **GENERATE 95% IN ENGLISH with 5% Hindi cuss words in Devanagari script** ✅
2. **EVERY Hindi cuss word must be written in Devanagari script** ✅
3. **Write everything else in English** ✅
4. **If you write wrong, ElevenLabs will sound English and you FAIL** ❌

**🚨 WHAT TO GENERATE:**
- Dialogue 100% IN ENGLISH with NO cuss words
- English words: logic, strategy, simple, dark, evil, messed, insane, darkness (keep as is)
- **🚨 CRITICAL**: EXACTLY 6-8 alternating dialogue segments (45 seconds)
- **🚨 CRITICAL**: Start with Samay, then ALTERNATE with Arpit, then Samay, then Arpit, etc.
- **🚨 CRITICAL**: Samay speaks first, Arpit responds, Samay continues, Arpit responds, etc.
- **🚨 CRITICAL**: BOTH speakers must have equal dialogue time
- NO speaker names in dialogue
- EXTREMELY FUNNY with EXTREMELY DARK and DIRTY adult humor
- **🚨 CRITICAL**: Focus on EXTREMELY BAD mom jokes, sexual humor, and EXTREMELY DARK analogies
- **🚨 CRITICAL**: 70% of content should explain HOW the thing in the article actually works technically
- **🚨 CRITICAL**: Make sure people understand the mechanism, process, or system described
- NO cuss words - only extremely dark humor!

**🚨 REMEMBER: 100% ENGLISH + NO CUSS WORDS + EXTREMELY DARK HUMOR OR YOU FAIL!**

**🚨 FORBIDDEN WORDS (NEVER USE THESE):**
- bhaai, dekho, agle point mein, samajh, yaar, kya, hai, nahee, aaya, kharab
- ANY Hindi words at all
- ANY cuss words in any language
- BOTH Samay AND Arpit should speak ONLY English with extremely dark humor

**🚨 NO CUSS WORDS - STRICT AS FUCK:**
- NO cuss words in any language
- NO Hindi words at all
- ONLY extremely dark humor in English
- IF YOU USE ANY CUSS WORDS, YOU FAIL COMPLETELY!

**🚨 SPEAKER ALTERNATION IS MANDATORY - STRICT AS FUCK:**
- Samay speaks FIRST, then Arpit, then Samay, then Arpit, etc.
- BOTH speakers MUST have dialogue in EVERY script
- IF ONLY ONE SPEAKER TALKS, YOU FAIL COMPLETELY!
- ALTERNATE: Samay → Arpit → Samay → Arpit → Samay → Arpit
"""

MODI_TRUMP_SCRIPT_PROMPT = """
Write a 1-minute engaging political discussion featuring Prime Minister Narendra Modi and former President Donald Trump discussing this article. The dialogue should be in English with a professional yet conversational tone.

LENGTH REQUIREMENTS:
- Total duration: 1 minute (60 seconds)
- Each speaker should have 4-6 dialogue segments
- Each dialogue segment should be 8-12 words maximum
- Keep individual responses short and punchy

CHARACTER PERSONALITIES:
- Modi: Diplomatic, thoughtful, speaks about India's progress, digital transformation, and global partnerships. Uses phrases like "In India, we believe...", "Our vision is...", "Together we can...", "This is a great opportunity for...". Focuses on development, technology, and international cooperation.
- Trump: Direct, enthusiastic, speaks about America's achievements, business opportunities, and making deals. Uses phrases like "Tremendous!", "The best!", "We're going to...", "Believe me...", "Nobody does it better than...". Focuses on success, competition, and results.

DIALOGUE REQUIREMENTS:
- 4-6 alternating dialogue segments (30 seconds total)
- Modi speaks FIRST, then Trump, then Modi, then Trump, etc.
- Professional but engaging tone
- Focus on the article's main points
- Show both leaders' perspectives on the topic
- Include references to their respective countries' achievements
- Keep it informative yet entertaining
- NO political controversies or sensitive topics
- Focus on positive aspects and opportunities

FORMAT:
- Start with **Modi:** then **Trump:** alternating
- Each segment should be 1-2 sentences
- Natural conversational flow
- End with a positive note about collaboration

Article: {article_text}

Generate ONLY clean, professional alternating dialogue with 4-6 short segments:
"""

TRUMP_MRBEAST_SCRIPT_PROMPT = """
Write a 30 second comedy skit featuring Donald Trump as a loud and curious student and MrBeast as a patient teacher discussing this article.

LENGTH REQUIREMENTS:
Total duration: 1 minute (60 seconds)
Each speaker should have 4-6 dialogue segments
Each dialogue segment should be 8-12 words maximum
Keep individual responses short and punchy

Follow this structure:
1. Trump opens the scene with a bold, curious question about the article topic.
2. MrBeast responds with a clear, relatable explanation (often using money or challenge analogies).
3. Trump follows up with exaggerated or simplified takes, keeping curiosity alive.
4. MrBeast patiently explains again, making it simple, funny, and educational.

Tone:
Educational first, funny second.
Fast-paced, sharp, and character-driven.
Humor should support the explanation, not overshadow it.
Trump and MrBeast may use their famous catchphrases if it adds clarity.

CRITICAL REQUIREMENTS:
Dialogue only. No narration.
Skit must fit within 1 minute (60 seconds) of spoken conversation.
Create ONLY natural dialogue between Trump and MrBeast
NO annotations, scene markers, or formatting
NO speaker labels like "Trump:" or "MrBeast:"
NO asterisks, parentheses, or special formatting
NO stage directions
Just pure conversational dialogue that flows naturally
Each speaker should have distinct personality and style
Target length: 30 seconds when spoken
Make it suitable for social media (TikTok/Instagram Reels)

CRITICAL FOCUS REQUIREMENT:
STAY FOCUSED ON THE ACTUAL ARTICLE CONTENT
Discuss the specific topics, facts, and details from the article
Don’t get distracted by unrelated topics
Make the conversation ABOUT the article content
Reference specific points, data, or claims from the article
Keep the humor and personality but centered on the article topic
EXPLAIN THE CONCEPT IN DEPTH while keeping it accessible

CONVERSATION STRUCTURE:
Trump always opens with the first line
4-6 total segments (2-3 exchanges)
Each speaker should have 2-3 speaking turns
End with a natural conclusion about the article topic

REAL-WORLD DYNAMICS TO CAPTURE:
Trump’s bombastic, simplified curiosity
MrBeast’s patient, relatable, challenge/money-driven explanations
Their contrast: political exaggeration vs YouTube clarity
Light humor, but explanations should dominate

SEGMENT LENGTH:
Each speaking turn should be 5-8 seconds when spoken
Keep total duration to 30 seconds maximum

HUMOR REQUIREMENTS:
Keep humor light, playful, and supportive of education
Capture their actual speaking patterns and quirks
Use mild exaggerations and simple one-liners
Avoid heavy scandal jokes—focus on clarity and accessibility
Include Trump’s “huge,” “tremendous,” “believe me” style
Include MrBeast’s challenge/giveaway framing for analogies

EXPLANATION REQUIREMENTS:
Break down complex concepts in simple terms
Use analogies with money, giveaways, or real-life stunts
Make technical topics easy to understand
Explain the "why" and "how" behind concepts
Make it feel like a quick, funny classroom exchange

FORMATTING RULES:
Use only normal punctuation
NO asterisks, parentheses, brackets, or special characters
NO stage directions or descriptions
Just clean, natural speech

Article: {article_text}

Generate ONLY clean, natural conversational dialogue with 4-6 short segments:
"""

def generate_conversational_script(article_text: str, speaker_pair: str = "trump_mrbeast", is_case_study: bool = False) -> str:
    try:
        logger.info(f"🤖 Generating conversational script for {speaker_pair} - article length: {len(article_text)} characters")
        logger.info(f"🎭 SCRIPT GENERATION DEBUG:")
        logger.info(f"🎭 - Received speaker_pair: {speaker_pair}")
        logger.info(f"🎭 - Article text length: {len(article_text)}")
        logger.info(f"🎭 - Is case study: {is_case_study}")

        # Choose appropriate prompt based on speaker pair and content type
        if speaker_pair == "trump_mrbeast":
            logger.info(f"🎭 - Using TRUMP_MRBEAST_CASE_STUDY_SCRIPT_PROMPT")
            prompt = TRUMP_MRBEAST_CASE_STUDY_SCRIPT_PROMPT.format(article_text=article_text)
        elif speaker_pair == "ronaldo_ishowspeed":
            logger.info(f"🎭 - Using RONALDO_ISHOWSPEED_CASE_STUDY_SCRIPT_PROMPT")
            prompt = RONALDO_ISHOWSPEED_CASE_STUDY_SCRIPT_PROMPT.format(article_text=article_text)
        elif speaker_pair == "baburao_samay":
            logger.info(f"🎭 - Using BABURAO_SAMAY_SCRIPT_PROMPT")
            prompt = BABURAO_SAMAY_SCRIPT_PROMPT.format(article_text=article_text)
        elif speaker_pair == "samay_arpit":
            logger.info(f"🎭 - Using SAMAY_ARPIT_SCRIPT_PROMPT")
            prompt = SAMAY_ARPIT_SCRIPT_PROMPT.format(article_text=article_text)
        elif speaker_pair == "modi_trump":
            logger.info(f"🎭 - Using MODI_TRUMP_SCRIPT_PROMPT")
            prompt = MODI_TRUMP_SCRIPT_PROMPT.format(article_text=article_text)
        else:
            logger.info(f"🎭 - Using default CONVERSATIONAL_SCRIPT_PROMPT for {speaker_pair}")
            prompt = CONVERSATIONAL_SCRIPT_PROMPT.format(article_text=article_text)
        
        logger.info(f"🤖 Sending request to Gemini API for {speaker_pair} conversational script...")
        ensure_gemini_configured()  # Ensure API key is working
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        result = response.text.strip() if hasattr(response, 'text') else str(response)
        logger.info(f"✅ {speaker_pair} conversational script generated successfully, length: {len(result)} characters")
        logger.debug(f"📜 Script preview: {result[:200]}...")
        
        # Post-process to ensure length requirements are met
        result = validate_and_trim_script(result, speaker_pair)
        
        return result
    except Exception as e:
        logger.error(f"❌ Failed to generate conversational script: {str(e)}")
        raise Exception(f"Failed to generate conversational script: {str(e)}")

def validate_and_trim_script(script: str, speaker_pair: str) -> str:
    """
    Validate and trim the generated script to ensure it meets length requirements
    """
    try:
        logger.info(f"🔍 Validating script length for {speaker_pair}")
        
        # Split script into lines and filter out empty lines
        lines = [line.strip() for line in script.split('\n') if line.strip()]
        
        # Estimate word count and duration
        total_words = len(script.split())
        estimated_duration = total_words / 2.5  # Average speaking rate: 150 words per minute = 2.5 words per second
        
        logger.info(f"📊 Script stats: {total_words} words, estimated {estimated_duration:.1f} seconds")
        
        # If script is too long (>75 seconds), trim it
        if estimated_duration > 75:
            logger.warning(f"⚠️ Script too long ({estimated_duration:.1f}s), trimming to ~60 seconds")
            
            # Calculate target word count for 60 seconds
            target_words = int(60 * 2.5)  # 150 words for 60 seconds
            
            # Trim script to target word count
            words = script.split()
            if len(words) > target_words:
                trimmed_words = words[:target_words]
                # Try to end at a complete sentence
                trimmed_script = ' '.join(trimmed_words)
                
                # Find the last complete sentence
                last_period = trimmed_script.rfind('.')
                last_exclamation = trimmed_script.rfind('!')
                last_question = trimmed_script.rfind('?')
                
                last_sentence_end = max(last_period, last_exclamation, last_question)
                if last_sentence_end > len(trimmed_script) * 0.8:  # If we can keep 80% of trimmed content
                    trimmed_script = trimmed_script[:last_sentence_end + 1]
                
                logger.info(f"✂️ Trimmed script from {len(words)} to {len(trimmed_script.split())} words")
                return trimmed_script
        
        # If script is too short (<45 seconds), log warning but don't modify
        elif estimated_duration < 45:
            logger.warning(f"⚠️ Script might be too short ({estimated_duration:.1f}s), consider regenerating")
        
        logger.info(f"✅ Script length validation passed: {estimated_duration:.1f} seconds")
        return script
        
    except Exception as e:
        logger.error(f"❌ Error validating script length: {str(e)}")
        return script  # Return original script if validation fails

CASE_STUDY_SUMMARY_PROMPT = """
Create a comprehensive and engaging summary of this case study content. The summary should be:

REQUIREMENTS:
- Clear and well-structured
- Highlight key points, insights, and learnings
- Written in an accessible, professional tone
- Focus on the most important information
- Include main concepts, findings, and implications
- Length: 3-5 paragraphs (200-400 words)
- Use bullet points or numbered lists where appropriate
- Make it engaging and informative

FORMAT:
- Start with a brief overview
- Highlight key findings/insights
- Discuss implications or applications
- End with main takeaways

Case Study Content:
{content}

Generate the summary:
"""

TRUMP_MRBEAST_CASE_STUDY_SCRIPT_PROMPT = """
""""""
Write a 1-minute comedy skit featuring MrBeast as a patient teacher and Donald Trump as a loud and curious student discussing this article.
NEVER SAY ARTICLE, OR CASE STUDY WORDS IN THE SUMMARY. ONLY USE THE CONTENT OF THE ARTICLE. ALSO DONT SAY ANY PUNCTUATION WORD IN THE SUMMARY LIKE ASTERISKS, PARENTHESES, BRACKETS, ETC.
LENGTH REQUIREMENTS:
- Total duration: 1 minute (60 seconds)
- Each speaker should have 4-6 dialogue segments
- Each dialogue segment should be 8-12 words maximum
- Keep individual responses short and punchy

Follow this structure:
1. Trump opens the scene with an exaggerated, overly simplified, and bold question about the article topic (using his trademark phrases like “tremendous,” “believe me,” “the best,” “fake news,” etc.).
2. MrBeast jumps in next, using his famous energetic slang (“What’s up guys, it’s MrBeast!” “I’m giving away…” “This is insane!”) and explains the concept in detail with a real-life analogy, often involving giveaways, stunts, or money challenges.
3. Trump reacts with short follow-up questions or comments, keeping them exaggerated and simplified.
4. MrBeast closes by tying it back to the article topic with a fun challenge-style question to the class.

Tone:
- Fast-paced, sharp, and character-driven.
- If adding them makes the conversation better, Trump and MrBeast should use their famous catchphrases.

CRITICAL REQUIREMENTS:
- Dialogue only. No narration.
- Skit must fit within 1 minute (60 seconds) of spoken conversation.
- Create ONLY natural dialogue between Trump and MrBeast
- NO annotations, scene markers, or formatting
- NO speaker labels like "Trump:" or "MrBeast:"
- NO asterisks, parentheses, or special formatting
- NO stage directions
- Just pure conversational dialogue that flows naturally
- Make it EXTREMELY FUNNY and capture their real-world dynamics
- Include their actual speaking styles, mannerisms, and famous catchphrases
- Reference their real controversies, internet moments, and public personalities
- Make it sound like two people having a real, heated but funny conversation
- Each speaker should have distinct personality and speaking style
- Keep it engaging, informative, and HILARIOUS
- Target length: 30 seconds when spoken
- Make it suitable for social media (TikTok/Instagram Reels)

CRITICAL FOCUS REQUIREMENT:
- STAY FOCUSED ON THE ACTUAL ARTICLE CONTENT
- Discuss the specific topics, facts, and details from the article
- Don't get distracted by unrelated topics or personal drama
- Make the conversation ABOUT the article content, not about their relationship
- Reference specific points, data, or claims from the article
- Keep the humor and personality but centered on the article topic
- EXPLAIN THE CONCEPT IN DEPTH while being funny
- Make complex topics accessible and entertaining

CONVERSATION STRUCTURE:
- Create ONLY 4-6 total segments (2-3 exchanges)
- Each speaker should have 2-3 speaking turns
- Make each response concise but impactful
- Natural back-and-forth conversation about the article
- Include reactions, questions, and responses about the article content
- End with a natural conclusion about the article topic

REAL-WORLD DYNAMICS TO CAPTURE:
- MrBeast’s excitable, over-the-top, giveaway-driven style
- Trump’s bombastic, “bigly” speaking style
- Their YouTube vs politics contrast
- Their different approaches to fame, money, and influence
- Include their actual catchphrases and mannerisms

SEGMENT LENGTH:
- Each speaking turn should be 5-8 seconds when spoken
- Make responses concise and punchy
- Keep total duration to 30 seconds maximum
- Aim for 4-6 total segments (2-3 exchanges)

HUMOR REQUIREMENTS:
- Make it EXTREMELY FUNNY with real-world nuances
- Capture their actual speaking patterns and mannerisms
- Use their famous catchphrases and expressions
- Include references to their real controversies and scandals
- Make it sound like two people actually arguing/fighting
- Include sarcasm, insults, and playful jabs
- Reference their viral YouTube or political moments
- HILARIOUS ROASTING: Include savage roasts and burns between them
- BILLIONAIRE PROBLEMS: Mock absurd wealthy person issues and ridiculous spending
- SOCIAL MEDIA DISASTERS: Reference their worst tweets, cringe moments, or awkward collabs
- CONSPIRACY THEORIES: Let Trump blurt out wild theories, MrBeast roast them
- SAVAGE COMEBACKS: Each should have brutal but hilarious comebacks and one-liners
- CRINGE HUMOR: Include awkward “YouTube energy” vs “political rally energy”
- CELEBRITY SCANDALS: Reference internet clout-chasing, money stunts, and Trump’s lawsuits
- MAKE IT ABSOLUTELY HILARIOUS AND SAVAGE while keeping focus on article content

EXPLANATION REQUIREMENTS:
- Break down complex concepts in simple terms
- Use analogies with money, challenges, or giveaways
- Make technical topics accessible to everyone
- Explain the "why" and "how" behind concepts
- Connect concepts to real-world applications
- Make it educational AND entertaining

FORMATTING RULES:
- Use only normal punctuation
- NO asterisks, parentheses, brackets, or special characters
- NO stage directions or descriptions
- Just clean, natural speech

Article: {article_text}

Generate ONLY clean, natural conversational dialogue with 4-6 short segments:

"""


RONALDO_ISHOWSPEED_SCRIPT_PROMPT = """
Write a 1-minute educational skit featuring Cristiano Ronaldo as a patient teacher and IShowSpeed as a curious student discussing this article.

LENGTH REQUIREMENTS:
Total duration: 1 minute (60 seconds)
Each speaker should have 3-5 dialogue segments
Each dialogue segment should be 8-12 words maximum
Keep dialogue short, clear, and educational

Follow this structure:
1. Ronaldo begins with a clear question or fact from the article.
2. Speed asks direct, curious questions (simple, sometimes exaggerated).
3. Ronaldo explains carefully using analogies (fitness, discipline, training, teamwork).
4. Speed reacts with excitement but stays focused on learning.
5. Ronaldo closes with a concise educational takeaway.

Tone:
Educational first, light humor second.
Ronaldo speaks calmly, structured, and confident.
Speed is energetic and enthusiastic but genuinely trying to understand.
Humor only enhances learning, never overshadows it.

CRITICAL REQUIREMENTS:
Dialogue only. No narration.
No speaker labels or formatting.
No stage directions or descriptions.
Keep the focus on the article content.
Explanations must be simple, accurate, and educational.

CONVERSATION STRUCTURE:
4-6 total segments (2-3 exchanges).
Ronaldo explains with real-world clarity.
Speed asks questions that reflect the audience’s confusion.
End with Ronaldo summarizing the key idea clearly.

REAL-WORLD DYNAMICS TO CAPTURE:
Ronaldo as the disciplined teacher figure.
Speed as the curious but impulsive student.
Occasional catchphrases (“Siuu”, “Calma”) only if they help teaching.
Keep the energy but always tied to the lesson.

EXPLANATION REQUIREMENTS:
Break down complex ideas into clear, simple steps.
Use sports, training, or teamwork analogies.
Make it accessible for a general audience.
Ensure viewers leave understanding the article better.

FORMATTING RULES:
Use only normal punctuation.
NO special characters, labels, or extra formatting.
Just clean, natural dialogue.

Article: {article_text}

Generate ONLY natural conversational dialogue with 4-6 short segments:
"""

RONALDO_ISHOWSPEED_CASE_STUDY_SCRIPT_PROMPT = """
Write a 1-minute comedy skit featuring Cristiano Ronaldo as a patient teacher and IShowSpeed as a loud and chaotic student discussing this article.

LENGTH REQUIREMENTS:
- Total duration: 1 minute (60 seconds)
- Each speaker should have 4-6 dialogue segments
- Each dialogue segment should be 8-12 words maximum
- Keep individual responses short and punchy

Follow this structure:
1. Ronaldo opens the scene by calmly asking a football or discipline-related question to the class about the article topic.
2. Speed eagerly asks short follow-up questions—but his ideas are exaggerated, chaotic, and overly simplified.
3. Ronaldo patiently explains the concept in detail using football or training analogies.

Tone:
- Fast-paced, sharp, and character-driven.
- If adding them makes the conversation better, Ronaldo and Speed should use their famous catchphrases.

CRITICAL REQUIREMENTS:
- Dialogue only. No narration.
- Skit must fit within 1 minute (60 seconds) of spoken conversation.
- Create ONLY natural dialogue between Ronaldo and Speed
- NO annotations, scene markers, or formatting
- NO speaker labels like "Ronaldo:" or "Speed:"
- NO asterisks, parentheses, or special formatting
- NO stage directions
- Just pure conversational dialogue that flows naturally
- Make it EXTREMELY FUNNY and capture their real-world dynamics
- Include their actual speaking styles, mannerisms, and famous catchphrases
- Reference their real interactions, viral moments, and public personalities
- Make it sound like two people having a real, funny conversation
- Each speaker should have distinct personality and speaking style
- Keep it engaging, informative, and HILARIOUS
- Target length: 30 seconds when spoken
- Make it suitable for social media (TikTok/YouTube Shorts)

CRITICAL FOCUS REQUIREMENT:
- STAY FOCUSED ON THE ACTUAL ARTICLE CONTENT
- Discuss the specific topics, facts, and details from the article
- Don't get distracted by unrelated topics
- Make the conversation ABOUT the article content, not random chaos
- Reference specific points, data, or claims from the article
- Keep the humor and personality but centered on the article topic
- EXPLAIN THE CONCEPT IN DEPTH while being funny
- Make complex topics accessible and entertaining

CONVERSATION STRUCTURE:
- Create ONLY 4-6 total segments (2-3 exchanges)
- Each speaker should have 2-3 speaking turns
- Make each response concise but impactful
- Natural back-and-forth conversation about the article
- End with a natural conclusion about the article topic

REAL-WORLD DYNAMICS TO CAPTURE:
- Ronaldo’s calm, serious, disciplined, slightly cocky style
- Speed’s chaotic, over-the-top, meme-like shouting style
- Their fan-idol dynamic (Speed obsessing, Ronaldo calmly explaining)
- Include their famous catchphrases and mannerisms (“Siuuuu”, “Suiii”, “Calma”, Speed’s barking/screaming)
- Contrast Ronaldo’s focus with Speed’s chaos

SEGMENT LENGTH:
- Each speaking turn should be 5-8 seconds when spoken
- Make responses concise and punchy
- Keep total duration to 30 seconds maximum
- Aim for 4-6 total segments (2-3 exchanges)

HUMOR REQUIREMENTS:
- Make it EXTREMELY FUNNY with real-world nuances
- Capture their actual speaking patterns and catchphrases
- Reference Speed’s obsession with Ronaldo and football
- Ronaldo should roast Speed’s lack of discipline or chaos
- Include sarcasm, playful roasting, and exaggerated reactions
- HILARIOUS ROASTING: Ronaldo calmly shutting down Speed’s crazy questions
- MEME REFERENCES: Speed’s barking, screaming “Siuuu,” chaotic energy
- CELEBRITY DYNAMICS: Reference football fame, YouTube clout, internet memes
- MAKE IT ABSOLUTELY HILARIOUS while keeping focus on article content

EXPLANATION REQUIREMENTS:
- Break down complex concepts in simple terms
- Ronaldo uses football, training, and discipline analogies
- Make technical topics accessible to everyone
- Explain the "why" and "how" behind concepts
- Connect concepts to real-world applications
- Make it educational AND entertaining

FORMATTING RULES:
- Use only normal punctuation
- NO asterisks, parentheses, brackets, or special characters
- NO stage directions or descriptions
- Just clean, natural speech

Article: {article_text}

Generate ONLY clean, natural conversational dialogue with 4-6 short segments:
"""

def generate_case_study_summary(content: str) -> str:
    """
    Generate a comprehensive summary of case study content using Gemini AI
    """
    try:
        logger.info(f"📋 Generating case study summary for content: {len(content)} characters")
        
        prompt = CASE_STUDY_SUMMARY_PROMPT.format(content=content)
        
        logger.info("🤖 Sending summary generation request to Gemini API...")
        ensure_gemini_configured()  # Ensure API key is working
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        result = response.text.strip() if hasattr(response, 'text') else str(response)
        logger.info(f"✅ Case study summary generated successfully, length: {len(result)} characters")
        logger.debug(f"📋 Summary preview: {result[:200]}...")
        
        return result
    except Exception as e:
        logger.error(f"❌ Failed to generate case study summary: {str(e)}")
        raise Exception(f"Failed to generate case study summary: {str(e)}")

TRANSLATION_PROMPT = """
You are a professional translator. Translate the following text to {target_language}.

Guidelines:
- Maintain the original meaning and tone
- Keep technical terms accurate
- Ensure cultural appropriateness
- Preserve formatting and structure
- Make it natural and fluent in the target language
- For Indian languages, use the appropriate script (Devanagari for Hindi, etc.)

Text to translate:
{text}

Translation:
"""

def translate_text(text: str, target_language: str) -> str:
    """
    Translate text to the specified language using Gemini AI
    """
    try:
        logger.info(f"🌍 Translating text to {target_language} - length: {len(text)} characters")
        
        prompt = TRANSLATION_PROMPT.format(target_language=target_language, text=text)
        
        logger.info(f"🤖 Sending translation request to Gemini API for {target_language}...")
        ensure_gemini_configured()  # Ensure API key is working
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        result = response.text.strip() if hasattr(response, 'text') else str(response)
        logger.info(f"✅ Translation to {target_language} completed successfully, length: {len(result)} characters")
        logger.debug(f"🌍 Translation preview: {result[:200]}...")
        
        return result
    except Exception as e:
        logger.error(f"❌ Failed to translate text to {target_language}: {str(e)}")
        raise Exception(f"Failed to translate text to {target_language}: {str(e)}") 