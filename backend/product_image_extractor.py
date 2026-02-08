import requests
from bs4 import BeautifulSoup
from PIL import Image as PILImage
import io
import logging
from typing import Optional, List
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)

def extract_product_images(product_url: str, max_images: int = 3) -> List[PILImage.Image]:
    """
    Extract product images from a fashion e-commerce URL.
    
    Args:
        product_url: URL of the product page
        max_images: Maximum number of images to extract
        
    Returns:
        List of PIL Image objects
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none'
        }
        
        session = requests.Session()
        session.headers.update(headers)
        
        response = session.get(product_url, timeout=15, allow_redirects=True)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Common selectors for product images across different sites
        image_selectors = [
            'img[data-testid*="product"]',
            'img[class*="product"]',
            'img[class*="ProductImage"]',
            'img[alt*="product"]',
            '.product-image img',
            '.ProductImageCarousel img',
            '[data-test-id*="product"] img',
            'img[src*="product"]',
            'img[src*="cdn"]'
        ]
        
        images = []
        found_urls = set()
        
        for selector in image_selectors:
            img_tags = soup.select(selector)
            
            for img in img_tags:
                img_url = img.get('src') or img.get('data-src') or img.get('data-original')
                
                if not img_url:
                    continue
                    
                # Convert relative URLs to absolute
                if img_url.startswith('//'):
                    img_url = 'https:' + img_url
                elif img_url.startswith('/'):
                    img_url = urljoin(product_url, img_url)
                
                # Skip duplicates and non-image URLs
                if img_url in found_urls or not any(ext in img_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                    continue
                    
                found_urls.add(img_url)
                
                try:
                    # Download and convert image
                    img_response = requests.get(img_url, headers=headers, timeout=5)
                    img_response.raise_for_status()
                    
                    image = PILImage.open(io.BytesIO(img_response.content))
                    
                    # Filter out small images (likely thumbnails)
                    if image.width >= 200 and image.height >= 200:
                        images.append(image)
                        logger.info(f"Extracted product image: {img_url}")
                        
                        if len(images) >= max_images:
                            break
                            
                except Exception as e:
                    logger.warning(f"Failed to download image {img_url}: {e}")
                    continue
            
            if len(images) >= max_images:
                break
        
        logger.info(f"Successfully extracted {len(images)} product images")
        return images
        
    except Exception as e:
        logger.error(f"Failed to extract product images from {product_url}: {e}")
        return []
