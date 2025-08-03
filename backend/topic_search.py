#!/usr/bin/env python3
"""
Topic search module for finding relevant articles about any topic
"""

import requests
import logging
from typing import List, Dict, Optional
from urllib.parse import quote_plus, urljoin
from bs4 import BeautifulSoup
import re
from article_extractor import ArticleExtractor

# Configure logging
logger = logging.getLogger(__name__)

class TopicSearcher:
    """
    Search for articles about any topic and extract their content
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.article_extractor = ArticleExtractor()
    
    def search_topic(self, topic: str, max_results: int = 5) -> List[Dict[str, str]]:
        """
        Search for articles about a topic
        Returns list of articles with URLs and titles
        """
        try:
            logger.info(f"🔍 Searching for topic: {topic}")
            
            # Search using DuckDuckGo (no API key required)
            search_results = self._search_duckduckgo(topic, max_results)
            
            if not search_results:
                # Fallback to Google search
                search_results = self._search_google(topic, max_results)
            
            logger.info(f"✅ Found {len(search_results)} articles for topic: {topic}")
            return search_results
            
        except Exception as e:
            logger.error(f"❌ Failed to search for topic '{topic}': {str(e)}")
            return []
    
    def _search_duckduckgo(self, topic: str, max_results: int) -> List[Dict[str, str]]:
        """Search using DuckDuckGo"""
        try:
            # Add terms to find quality articles
            enhanced_query = f"{topic} article explanation guide"
            search_url = f"https://duckduckgo.com/html/?q={quote_plus(enhanced_query)}"
            
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            results = []
            # Look for result links in DuckDuckGo's HTML structure
            result_links = soup.find_all('a', class_='result__url')
            
            for link in result_links[:max_results]:
                url = link.get('href')
                if url and self._is_valid_article_url(url):
                    # Get title from the parent result container
                    result_container = link.find_parent('div', class_='result__body')
                    if result_container:
                        title_element = result_container.find('a', class_='result__a')
                        title = title_element.get_text().strip() if title_element else "Article"
                    else:
                        title = "Article"
                    
                    results.append({
                        'url': url,
                        'title': title,
                        'source': 'DuckDuckGo'
                    })
            
            return results
            
        except Exception as e:
            logger.warning(f"⚠️ DuckDuckGo search failed: {str(e)}")
            return []
    
    def _search_google(self, topic: str, max_results: int) -> List[Dict[str, str]]:
        """Fallback Google search"""
        try:
            # Add terms to find quality articles
            enhanced_query = f"{topic} article explanation guide tutorial"
            search_url = f"https://www.google.com/search?q={quote_plus(enhanced_query)}"
            
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            results = []
            # Look for search result links
            link_elements = soup.find_all('a', href=True)
            
            for element in link_elements:
                href = element.get('href')
                if href and href.startswith('/url?q='):
                    # Extract actual URL from Google's redirect
                    url = href.split('/url?q=')[1].split('&')[0]
                    if self._is_valid_article_url(url):
                        title = element.get_text().strip() or "Article"
                        results.append({
                            'url': url,
                            'title': title,
                            'source': 'Google'
                        })
                        
                        if len(results) >= max_results:
                            break
            
            return results
            
        except Exception as e:
            logger.warning(f"⚠️ Google search failed: {str(e)}")
            return []
    
    def _is_valid_article_url(self, url: str) -> bool:
        """Check if URL is likely to contain a good article"""
        if not url or not url.startswith(('http://', 'https://')):
            return False
        
        # Skip social media and video platforms
        skip_domains = [
            'facebook.com', 'twitter.com', 'instagram.com', 'tiktok.com',
            'youtube.com', 'youtu.be', 'reddit.com', 'pinterest.com'
        ]
        
        for domain in skip_domains:
            if domain in url.lower():
                return False
        
        # Prefer quality content sources
        quality_domains = [
            'wikipedia.org', 'medium.com', 'techcrunch.com', 'wired.com',
            'arstechnica.com', 'github.com', 'stackoverflow.com', 'forbes.com',
            'bbc.com', 'cnn.com', 'reuters.com', 'bloomberg.com', 'theatlantic.com',
            'newyorker.com', 'economist.com', 'harvard.edu', 'mit.edu', 'stanford.edu'
        ]
        
        for domain in quality_domains:
            if domain in url.lower():
                return True
        
        # General article indicators
        article_indicators = [
            'article', 'blog', 'post', 'guide', 'tutorial', 'explanation',
            'news', 'research', 'paper', 'study'
        ]
        
        for indicator in article_indicators:
            if indicator in url.lower():
                return True
        
        return True  # Default to allowing URLs
    
    def find_best_article_for_topic(self, topic: str) -> Optional[Dict[str, str]]:
        """
        Find the best article about a topic and extract its content
        """
        try:
            logger.info(f"🎯 Finding best article for topic: {topic}")
            
            # Search for articles
            search_results = self.search_topic(topic, max_results=10)
            
            if not search_results:
                logger.warning(f"⚠️ No articles found for topic: {topic}")
                return None
            
            # Try to extract content from each article until we find a good one
            for i, result in enumerate(search_results):
                try:
                    logger.info(f"📖 Trying to extract content from article {i+1}/{len(search_results)}: {result['url']}")
                    
                    article_data = self.article_extractor.extract_article_content(result['url'])
                    
                    # Check if we got good content
                    if len(article_data['content']) > 500:  # Minimum content length
                        logger.info(f"✅ Successfully extracted good content from: {result['url']}")
                        logger.info(f"📄 Content length: {len(article_data['content'])} characters")
                        
                        # Add search metadata
                        article_data['search_topic'] = topic
                        article_data['search_rank'] = i + 1
                        article_data['search_source'] = result.get('source', 'Unknown')
                        
                        return article_data
                    else:
                        logger.warning(f"⚠️ Content too short from {result['url']}, trying next...")
                        
                except Exception as e:
                    logger.warning(f"⚠️ Failed to extract from {result['url']}: {str(e)}")
                    continue
            
            logger.error(f"❌ Could not extract good content from any article for topic: {topic}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to find article for topic '{topic}': {str(e)}")
            return None

def search_and_extract_topic(topic: str) -> Optional[Dict[str, str]]:
    """
    Convenience function to search for a topic and extract the best article
    """
    searcher = TopicSearcher()
    return searcher.find_best_article_for_topic(topic)