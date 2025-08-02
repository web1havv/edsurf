#!/usr/bin/env python3
"""
Article content extractor for any URL
Handles different website formats and content extraction
"""

import requests
import logging
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
from typing import Dict, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ArticleExtractor:
    """
    Extract article content from any URL
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def extract_article_content(self, url: str) -> Dict[str, str]:
        """
        Extract article content from URL
        Returns: {'title': str, 'content': str, 'summary': str}
        """
        try:
            logger.info(f"🔍 Extracting content from: {url}")
            
            # Fetch the webpage
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = self._extract_title(soup)
            
            # Extract main content
            content = self._extract_main_content(soup, url)
            
            # Generate summary
            summary = self._generate_summary(content)
            
            logger.info(f"✅ Successfully extracted article")
            logger.info(f"📝 Title: {title[:100]}...")
            logger.info(f"📄 Content length: {len(content)} characters")
            logger.info(f"📋 Summary length: {len(summary)} characters")
            
            return {
                'title': title,
                'content': content,
                'summary': summary,
                'url': url
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to extract article content: {str(e)}")
            raise Exception(f"Failed to extract article content: {str(e)}")
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract article title"""
        # Try multiple title selectors
        title_selectors = [
            'h1',
            'title',
            '[class*="title"]',
            '[class*="headline"]',
            'h2',
            'h3'
        ]
        
        for selector in title_selectors:
            elements = soup.select(selector)
            for element in elements:
                title = element.get_text().strip()
                if title and len(title) > 10 and len(title) < 200:
                    return title
        
        # Fallback to page title
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()
        
        return "Article"
    
    def _extract_main_content(self, soup: BeautifulSoup, url: str) -> str:
        """Extract main article content"""
        domain = urlparse(url).netloc.lower()
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'advertisement']):
            element.decompose()
        
        # Try domain-specific extraction
        if 'medium.com' in domain:
            return self._extract_medium_content(soup)
        elif 'techcrunch.com' in domain:
            return self._extract_techcrunch_content(soup)
        elif 'wired.com' in domain:
            return self._extract_wired_content(soup)
        elif 'arstechnica.com' in domain:
            return self._extract_arstechnica_content(soup)
        elif 'github.com' in domain:
            return self._extract_github_content(soup)
        elif 'stackoverflow.com' in domain:
            return self._extract_stackoverflow_content(soup)
        else:
            return self._extract_generic_content(soup)
    
    def _extract_medium_content(self, soup: BeautifulSoup) -> str:
        """Extract content from Medium articles"""
        content_selectors = [
            'article',
            '[class*="story"]',
            '[class*="post"]',
            '[class*="content"]'
        ]
        
        for selector in content_selectors:
            elements = soup.select(selector)
            for element in elements:
                paragraphs = element.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                if paragraphs:
                    content = ' '.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
                    if len(content) > 200:
                        return content
        
        return self._extract_generic_content(soup)
    
    def _extract_techcrunch_content(self, soup: BeautifulSoup) -> str:
        """Extract content from TechCrunch articles"""
        content_selectors = [
            'article',
            '[class*="article-content"]',
            '[class*="entry-content"]'
        ]
        
        for selector in content_selectors:
            elements = soup.select(selector)
            for element in elements:
                paragraphs = element.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                if paragraphs:
                    content = ' '.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
                    if len(content) > 200:
                        return content
        
        return self._extract_generic_content(soup)
    
    def _extract_wired_content(self, soup: BeautifulSoup) -> str:
        """Extract content from Wired articles"""
        content_selectors = [
            'article',
            '[class*="article-body"]',
            '[class*="content"]'
        ]
        
        for selector in content_selectors:
            elements = soup.select(selector)
            for element in elements:
                paragraphs = element.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                if paragraphs:
                    content = ' '.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
                    if len(content) > 200:
                        return content
        
        return self._extract_generic_content(soup)
    
    def _extract_arstechnica_content(self, soup: BeautifulSoup) -> str:
        """Extract content from Ars Technica articles"""
        content_selectors = [
            'article',
            '[class*="article-content"]',
            '[class*="entry-content"]'
        ]
        
        for selector in content_selectors:
            elements = soup.select(selector)
            for element in elements:
                paragraphs = element.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                if paragraphs:
                    content = ' '.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
                    if len(content) > 200:
                        return content
        
        return self._extract_generic_content(soup)
    
    def _extract_github_content(self, soup: BeautifulSoup) -> str:
        """Extract content from GitHub README or documentation"""
        content_selectors = [
            '#readme',
            '[class*="markdown"]',
            'article',
            'main'
        ]
        
        for selector in content_selectors:
            elements = soup.select(selector)
            for element in elements:
                paragraphs = element.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li'])
                if paragraphs:
                    content = ' '.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
                    if len(content) > 200:
                        return content
        
        return self._extract_generic_content(soup)
    
    def _extract_stackoverflow_content(self, soup: BeautifulSoup) -> str:
        """Extract content from Stack Overflow questions/answers"""
        content_selectors = [
            '.question',
            '.answer',
            '[class*="post-text"]',
            'article'
        ]
        
        for selector in content_selectors:
            elements = soup.select(selector)
            for element in elements:
                paragraphs = element.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                if paragraphs:
                    content = ' '.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
                    if len(content) > 200:
                        return content
        
        return self._extract_generic_content(soup)
    
    def _extract_generic_content(self, soup: BeautifulSoup) -> str:
        """Generic content extraction for any website"""
        # Try to find the main content area
        main_selectors = [
            'main',
            'article',
            '[role="main"]',
            '[class*="content"]',
            '[class*="article"]',
            '[class*="post"]',
            '[class*="entry"]'
        ]
        
        for selector in main_selectors:
            elements = soup.select(selector)
            for element in elements:
                paragraphs = element.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                if paragraphs:
                    content = ' '.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
                    if len(content) > 200:
                        return content
        
        # Fallback: get all paragraphs
        paragraphs = soup.find_all('p')
        if paragraphs:
            content = ' '.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
            if len(content) > 100:
                return content
        
        # Last resort: get all text
        text = soup.get_text()
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text[:5000]  # Limit to 5000 characters
    
    def _generate_summary(self, content: str) -> str:
        """Generate a brief summary of the content"""
        if len(content) <= 500:
            return content
        
        # Take first 500 characters and find a good ending point
        summary = content[:500]
        
        # Try to end at a sentence boundary
        last_period = summary.rfind('.')
        last_exclamation = summary.rfind('!')
        last_question = summary.rfind('?')
        
        end_points = [last_period, last_exclamation, last_question]
        end_points = [p for p in end_points if p > 0]
        
        if end_points:
            end_point = max(end_points)
            summary = summary[:end_point + 1]
        
        return summary

def extract_article_from_url(url: str) -> Dict[str, str]:
    """
    Convenience function to extract article content from URL
    """
    extractor = ArticleExtractor()
    return extractor.extract_article_content(url) 