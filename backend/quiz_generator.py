"""
Quiz Generation Module
Creates AI-powered quizzes from case study content
"""

import logging
import json
import uuid
from typing import Dict, List, Any
from datetime import datetime
import google.generativeai as genai
import os

logger = logging.getLogger(__name__)

# Configure Gemini API with the provided key
GEMINI_API_KEY = "AIzaSyBALLCySBJgG34579ZD3OehRoktbVyecGc"
genai.configure(api_key=GEMINI_API_KEY)

QUIZ_GENERATION_PROMPT = """
You are an expert quiz creator. Create a comprehensive 5-question quiz based on the provided case study content.

QUIZ REQUIREMENTS:
- Generate exactly 5 questions
- Each question should have 4 multiple choice options (A, B, C, D)
- Questions should test understanding of key concepts, facts, and insights from the case study
- Mix different types of questions: factual, analytical, and application-based
- Ensure questions are clear, concise, and unambiguous
- Make sure there's only one correct answer per question
- Questions should be progressively challenging but fair

QUESTION TYPES TO INCLUDE:
1. Factual question (basic information from the case study)
2. Analytical question (understanding relationships or causes)
3. Application question (how concepts apply in different scenarios)
4. Critical thinking question (evaluation or synthesis)
5. Summary question (overall understanding of the case study)

OUTPUT FORMAT:
CRITICAL: Return ONLY valid JSON. No explanations, no markdown, no extra text. Just the JSON object.

Return a JSON object with this exact structure:
{{
    "quiz_id": "unique_quiz_id",
    "title": "Case Study Quiz",
    "description": "Test your understanding of the case study",
    "questions": [
        {{
            "question_id": 1,
            "question": "Question text here?",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": 0,
            "explanation": "Explanation of why this answer is correct"
        }}
    ]
}}

Case Study Content:
{content}

Generate ONLY the JSON object:
"""

def generate_quiz_from_content(content: str) -> Dict[str, Any]:
    """
    Generate a 5-question quiz from case study content using Gemini AI
    """
    try:
        logger.info(f"🧠 Generating quiz from content: {len(content)} characters")
        
        # Create unique quiz ID
        quiz_id = str(uuid.uuid4())
        
        # Prepare prompt
        prompt = QUIZ_GENERATION_PROMPT.format(content=content)
        
        logger.info("🤖 Sending quiz generation request to Gemini API...")
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        if not response or not hasattr(response, 'text'):
            raise Exception("No response from Gemini API")
        
        # Parse JSON response
        try:
            response_text = response.text.strip()
            
            # Try to extract JSON from the response if it's wrapped in markdown or has extra text
            if "```json" in response_text:
                # Extract JSON from markdown code block
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                if end != -1:
                    response_text = response_text[start:end].strip()
            elif "```" in response_text:
                # Extract JSON from code block
                start = response_text.find("```") + 3
                end = response_text.find("```", start)
                if end != -1:
                    response_text = response_text[start:end].strip()
            
            # Try to find JSON object boundaries
            if response_text.startswith("{"):
                # Find the end of the JSON object
                brace_count = 0
                json_end = 0
                for i, char in enumerate(response_text):
                    if char == "{":
                        brace_count += 1
                    elif char == "}":
                        brace_count -= 1
                        if brace_count == 0:
                            json_end = i + 1
                            break
                if json_end > 0:
                    response_text = response_text[:json_end]
            
            quiz_data = json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse quiz JSON: {str(e)}")
            logger.error(f"Raw response: {response.text}")
            raise Exception("Failed to parse quiz response as JSON")
        
        # Validate quiz structure
        if not validate_quiz_structure(quiz_data):
            raise Exception("Invalid quiz structure received from AI")
        
        # Add metadata
        quiz_data["quiz_id"] = quiz_id
        quiz_data["generated_at"] = datetime.now().isoformat()
        quiz_data["total_questions"] = len(quiz_data["questions"])
        
        logger.info(f"✅ Quiz generated successfully: {quiz_data['total_questions']} questions")
        logger.info(f"📊 Quiz ID: {quiz_id}")
        
        return quiz_data
        
    except Exception as e:
        logger.error(f"❌ Failed to generate quiz: {str(e)}")
        raise Exception(f"Failed to generate quiz: {str(e)}")

def validate_quiz_structure(quiz_data: Dict[str, Any]) -> bool:
    """
    Validate that the quiz has the correct structure
    """
    try:
        # Check required fields
        required_fields = ["title", "description", "questions"]
        for field in required_fields:
            if field not in quiz_data:
                logger.error(f"❌ Missing required field: {field}")
                return False
        
        # Check questions structure
        questions = quiz_data["questions"]
        if not isinstance(questions, list) or len(questions) != 5:
            logger.error(f"❌ Invalid questions: expected 5 questions, got {len(questions) if isinstance(questions, list) else 'not a list'}")
            return False
        
        # Check each question structure
        for i, question in enumerate(questions):
            required_question_fields = ["question", "options", "correct_answer"]
            for field in required_question_fields:
                if field not in question:
                    logger.error(f"❌ Question {i+1} missing field: {field}")
                    return False
            
            # Check options
            options = question["options"]
            if not isinstance(options, list) or len(options) != 4:
                logger.error(f"❌ Question {i+1} invalid options: expected 4 options, got {len(options) if isinstance(options, list) else 'not a list'}")
                return False
            
            # Check correct answer
            correct_answer = question["correct_answer"]
            if not isinstance(correct_answer, int) or correct_answer < 0 or correct_answer > 3:
                logger.error(f"❌ Question {i+1} invalid correct_answer: expected 0-3, got {correct_answer}")
                return False
        
        logger.info("✅ Quiz structure validation passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Quiz validation error: {str(e)}")
        return False

def calculate_quiz_score(quiz_data: Dict[str, Any], user_answers) -> Dict[str, Any]:
    """
    Calculate quiz score and generate detailed results
    """
    try:
        logger.info(f"📊 Calculating quiz score for {len(user_answers)} answers")
        
        # Convert list to dictionary if needed
        if isinstance(user_answers, list):
            user_answers_dict = {i: answer for i, answer in enumerate(user_answers)}
        else:
            user_answers_dict = user_answers
        
        questions = quiz_data["questions"]
        total_questions = len(questions)
        correct_answers = 0
        question_results = []
        
        for i, question in enumerate(questions):
            user_answer = user_answers_dict.get(i, -1)  # -1 means no answer
            correct_answer = question["correct_answer"]
            is_correct = user_answer == correct_answer
            
            if is_correct:
                correct_answers += 1
            
            question_result = {
                "question_id": i + 1,
                "question": question["question"],
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "correct": is_correct,
                "explanation": question.get("explanation", "No explanation provided")
            }
            question_results.append(question_result)
        
        score_percentage = (correct_answers / total_questions) * 100
        
        results = {
            "quiz_id": quiz_data["quiz_id"],
            "score": correct_answers,
            "total_questions": total_questions,
            "percentage": round(score_percentage, 1),
            "question_results": question_results,
            "submitted_at": datetime.now().isoformat()
        }
        
        logger.info(f"✅ Quiz scored: {correct_answers}/{total_questions} ({score_percentage:.1f}%)")
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Failed to calculate quiz score: {str(e)}")
        raise Exception(f"Failed to calculate quiz score: {str(e)}")

def save_quiz_data(quiz_data: Dict[str, Any]) -> str:
    """
    Save quiz data to file for later retrieval
    """
    try:
        quiz_id = quiz_data["quiz_id"]
        filename = f"quiz_{quiz_id}.json"
        filepath = os.path.join("outputs", filename)
        
        # Ensure outputs directory exists
        os.makedirs("outputs", exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(quiz_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Quiz data saved: {filepath}")
        return filepath
        
    except Exception as e:
        logger.error(f"❌ Failed to save quiz data: {str(e)}")
        raise Exception(f"Failed to save quiz data: {str(e)}")

def load_quiz_data(quiz_id: str) -> Dict[str, Any]:
    """
    Load quiz data from file
    """
    try:
        filename = f"quiz_{quiz_id}.json"
        filepath = os.path.join("outputs", filename)
        
        if not os.path.exists(filepath):
            raise Exception(f"Quiz not found: {quiz_id}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            quiz_data = json.load(f)
        
        logger.info(f"📂 Quiz data loaded: {filepath}")
        return quiz_data
        
    except Exception as e:
        logger.error(f"❌ Failed to load quiz data: {str(e)}")
        raise Exception(f"Failed to load quiz data: {str(e)}")
