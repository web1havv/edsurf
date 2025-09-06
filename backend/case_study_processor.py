"""
Case Study Processing Module
Handles PDF extraction, text processing, and case study generation
"""

import os
import tempfile
import logging
from typing import Dict, Any
import PyPDF2
import docx
from datetime import datetime

logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text content from PDF file
    """
    try:
        logger.info(f"📄 Extracting text from PDF: {file_path}")
        
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
            
            logger.info(f"✅ PDF text extracted successfully: {len(text)} characters")
            return text.strip()
            
    except Exception as e:
        logger.error(f"❌ Failed to extract PDF text: {str(e)}")
        raise Exception(f"Failed to extract PDF text: {str(e)}")

def extract_text_from_docx(file_path: str) -> str:
    """
    Extract text content from DOCX file
    """
    try:
        logger.info(f"📄 Extracting text from DOCX: {file_path}")
        
        doc = docx.Document(file_path)
        text = ""
        
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        
        logger.info(f"✅ DOCX text extracted successfully: {len(text)} characters")
        return text.strip()
        
    except Exception as e:
        logger.error(f"❌ Failed to extract DOCX text: {str(e)}")
        raise Exception(f"Failed to extract DOCX text: {str(e)}")

def extract_text_from_file(file_path: str) -> str:
    """
    Extract text from various file formats
    """
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension == '.pdf':
        return extract_text_from_pdf(file_path)
    elif file_extension in ['.docx', '.doc']:
        return extract_text_from_docx(file_path)
    elif file_extension == '.txt':
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    else:
        raise Exception(f"Unsupported file format: {file_extension}")

def process_case_study_file(file_path: str, speaker_pair: str = None) -> Dict[str, Any]:
    """
    Process uploaded case study file and extract content
    """
    try:
        logger.info(f"📚 Processing case study file: {file_path}")
        
        # Extract text content
        content = extract_text_from_file(file_path)
        
        if not content or len(content.strip()) < 50:
            raise Exception("File appears to be empty or too short to process")
        
        # Generate summary using AI
        from llm import generate_case_study_summary
        summary = generate_case_study_summary(content)
        
        # Generate conversational script only if speaker pair is provided
        script = ""
        if speaker_pair:
            from llm import generate_conversational_script
            script = generate_conversational_script(content, speaker_pair, is_case_study=True)
        
        logger.info(f"✅ Case study processed successfully")
        logger.info(f"📊 Content length: {len(content)} characters")
        logger.info(f"📋 Summary length: {len(summary)} characters")
        logger.info(f"📜 Script length: {len(script)} characters")
        
        return {
            "content": content,
            "summary": summary,
            "script": script,
            "speaker_pair": speaker_pair,
            "processed_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to process case study file: {str(e)}")
        raise Exception(f"Failed to process case study file: {str(e)}")

def process_case_study_text(text: str, speaker_pair: str = None) -> Dict[str, Any]:
    """
    Process case study text content
    """
    try:
        logger.info(f"📚 Processing case study text: {len(text)} characters")
        
        if not text or len(text.strip()) < 50:
            raise Exception("Text appears to be empty or too short to process")
        
        # Generate summary using AI
        from llm import generate_case_study_summary
        summary = generate_case_study_summary(text)
        
        # Generate conversational script only if speaker pair is provided
        script = ""
        if speaker_pair:
            from llm import generate_conversational_script
            script = generate_conversational_script(text, speaker_pair, is_case_study=True)
        
        logger.info(f"✅ Case study text processed successfully")
        logger.info(f"📋 Summary length: {len(summary)} characters")
        logger.info(f"📜 Script length: {len(script)} characters")
        
        return {
            "content": text,
            "summary": summary,
            "script": script,
            "speaker_pair": speaker_pair,
            "processed_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to process case study text: {str(e)}")
        raise Exception(f"Failed to process case study text: {str(e)}")
