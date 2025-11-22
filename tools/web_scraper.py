import requests
from bs4 import BeautifulSoup
from typing import List, Optional
from models.schemas import SourceContent

class WebScraper:
    """Tool for scraping and parsing web content."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_url(self, url: str) -> Optional[SourceContent]:
        """Scrape and parse content from a URL."""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Try trafilatura first for cleaner content extraction
            content = self._extract_with_trafilatura(response.text, url)
            if not content:
                # Fallback to BeautifulSoup
                content = self._extract_with_bs4(response.text, url)
            
            return content
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None
    
    def _extract_with_trafilatura(self, html: str, url: str) -> Optional[SourceContent]:
        """Extract content using trafilatura."""
        try:
            from trafilatura import extract
            content = extract(html)
            if content:
                chunks = self._chunk_text(content)
                return SourceContent(
                    url=url,
                    title=self._extract_title_bs4(html),
                    content=content,
                    chunks=chunks,
                    metadata={'method': 'trafilatura'}
                )
        except ImportError:
            print("Trafilatura not available, using BeautifulSoup")
        except Exception as e:
            print(f"Trafilatura extraction failed: {e}")
        
        return None
    
    def _extract_with_bs4(self, html: str, url: str) -> SourceContent:
        """Extract content using BeautifulSoup."""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'footer']):
            element.decompose()
        
        title = self._extract_title_bs4(html)
        content = self._extract_content_bs4(soup)
        chunks = self._chunk_text(content)
        
        return SourceContent(
            url=url,
            title=title,
            content=content,
            chunks=chunks,
            metadata={'method': 'beautifulsoup'}
        )
    
    def _extract_title_bs4(self, html: str) -> str:
        """Extract page title using BeautifulSoup."""
        soup = BeautifulSoup(html, 'html.parser')
        title_tag = soup.find('title')
        return title_tag.get_text().strip() if title_tag else "No Title"
    
    def _extract_content_bs4(self, soup: BeautifulSoup) -> str:
        """Extract main content from page using BeautifulSoup."""
        # Try to find main content areas
        content_selectors = [
            'article',
            'main',
            '.content',
            '.main-content',
            '#content',
            '#main-content',
            'div[role="main"]'
        ]
        
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text().strip()
        
        # Fallback to body
        return soup.find('body').get_text().strip()
    
    def _chunk_text(self, text: str, chunk_size: int = 500) -> List[str]:
        """Split text into manageable chunks."""
        words = text.split()
        chunks = []
        current_chunk = []
        
        for word in words:
            current_chunk.append(word)
            if len(' '.join(current_chunk)) >= chunk_size:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks