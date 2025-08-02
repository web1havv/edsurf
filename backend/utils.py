import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

def extract_from_url(url):
    try:
        logger.info(f"🌐 Extracting content from URL: {url}")
        
        logger.info("📡 Making HTTP request...")
        resp = requests.get(url)
        
        logger.info(f"📡 HTTP response status: {resp.status_code}")
        if resp.status_code != 200:
            logger.warning(f"⚠️ Non-200 status code: {resp.status_code}")
        
        logger.info("🔍 Parsing HTML content...")
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Extract title
        title = soup.title.string if soup.title else ""
        logger.info(f"📄 Page title: {title[:100]}{'...' if len(title) > 100 else ''}")
        
        # Extract article content
        logger.info("📖 Looking for article content...")
        article = soup.find("article")
        
        if article:
            logger.info("✅ Found <article> tag, extracting content...")
            text = article.get_text(separator="\n")
        else:
            logger.info("⚠️ No <article> tag found, using <body> content...")
            text = soup.body.get_text(separator="\n") if soup.body else ""
        
        # Clean and format text
        logger.info(f"📝 Extracted text length: {len(text)} characters")
        logger.debug(f"📝 Text preview: {text[:200]}...")
        
        # Combine title and content
        result = f"{title}\n\n{text}"
        logger.info(f"✅ Content extraction completed. Total length: {len(result)} characters")
        
        return result
        
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Network error while fetching URL: {str(e)}")
        raise Exception(f"Failed to fetch URL: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Error extracting content from URL: {str(e)}")
        logger.error(f"❌ Error type: {type(e).__name__}")
        raise Exception(f"Failed to extract content from URL: {str(e)}") 