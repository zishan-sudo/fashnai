import logging
import uuid
import os
from textwrap import dedent
from typing import List, Optional, Dict
from agno.agent import Agent, RunOutput
from agno.models.google import Gemini
from agno.db.sqlite import SqliteDb
from agno.tools.serper import SerperTools
from agno.tools.crawl4ai import Crawl4aiTools
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from api_key_manager import api_key_manager

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(
    "%(asctime)s %(levelname)s [%(name)s] %(message)s"
))
logger.addHandler(handler)

load_dotenv()

# Use paid Gemini API key for all agents
llm = Gemini(
    id='gemini-2.5-flash',
    api_key=os.getenv("GOOGLE_API_KEY_1"),
    vertexai=False
)


class ProductSpecification(BaseModel):
    product_name: str = Field(default="Unknown", description="Full product name/title")
    brand: str = Field(default="Unknown", description="Brand name")
    category: str = Field(default="Unknown", description="Product category (e.g., Sneakers, Dress, Jacket)")
    color: str = Field(default="Unknown", description="Color or colorway")
    material: str = Field(default="Unknown", description="Primary material or fabric composition")
    sizes_available: List[str] = Field(default_factory=list, description="List of available sizes")
    care_instructions: Optional[str] = Field(None, description="Care and washing instructions")
    features: List[str] = Field(default_factory=list, description="Key product features (3-7 items)")
    dimensions: Optional[Dict[str, str]] = Field(None, description="Product dimensions if applicable")
    weight: Optional[str] = Field(None, description="Product weight if applicable")
    style_number: Optional[str] = Field(None, description="Style number, SKU, or product code")
    country_of_origin: Optional[str] = Field(None, description="Manufacturing country")
    sustainability: Optional[str] = Field(None, description="Sustainability or eco-friendly information")
    fit_type: Optional[str] = Field(None, description="Fit type (e.g., Regular Fit, Slim Fit, Oversized)")
    additional_specs: Dict[str, str] = Field(default_factory=dict, description="Any additional specifications")
    sources: List[str] = Field(default_factory=list, description="URLs where specifications were found")


def product_specs_agent() -> Agent:
    agent = Agent(
        name="Fashion Product Specifications Agent",
        model=llm,
        tools=[
            SerperTools(api_key=os.getenv("SERPER_API_KEY")),
            Crawl4aiTools(max_length=15000),
        ],
        tool_call_limit=15,
        description=dedent("""\
        You are an intelligent product specifications extraction agent specialized in fashion products. 
        Your job is to extract comprehensive, accurate product specifications from fashion e-commerce 
        websites including materials, sizes, care instructions, and technical details.
        """),
        instructions=dedent("""\
        You will receive a product URL. Your task is to:
        
        1. Product Information Extraction Phase
            - Crawl the provided product URL thoroughly
            - Extract basic information:
                * Full product name/title
                * Brand name
                * Product category (Sneakers, Dress, Jacket, Jeans, etc.)
                * Color/colorway
                * Style number or SKU
            
        2. Material & Construction Details
            - Extract material composition:
                * Primary materials (e.g., 100% Cotton, Leather, Polyester blend)
                * Fabric type (e.g., Denim, Jersey, Canvas)
                * Special treatments or finishes
            - Construction details:
                * Stitching type
                * Closure type (zipper, buttons, laces)
                * Lining information
        
        3. Sizing Information
            - List all available sizes (XS, S, M, L, XL, or numeric sizes)
            - Note fit type (Regular Fit, Slim Fit, Oversized, etc.)
            - Extract size chart information if available
            - Note any sizing recommendations
        
        4. Care Instructions
            - Washing instructions
            - Drying instructions
            - Ironing guidelines
            - Special care notes
        
        5. Product Features
            - Extract 3-7 key features:
                * Functional features (pockets, adjustable straps, etc.)
                * Design features (patterns, embellishments, etc.)
                * Performance features (waterproof, breathable, etc.)
                * Comfort features (cushioned, stretchy, etc.)
        
        6. Additional Specifications
            - Dimensions (length, width, height for bags/accessories)
            - Weight (if provided)
            - Country of origin/manufacturing
            - Sustainability information (recycled materials, eco-friendly, etc.)
            - Certifications (OEKO-TEX, Fair Trade, etc.)
        
        7. Search for Additional Information
            - If specifications are incomplete on the product page:
                * Search for the product on brand's official website
                * Search for product reviews that mention specifications
                * Search for retailer descriptions
            - Use search queries like:
                * "[Brand] [Product Name] specifications"
                * "[Product Name] material composition"
                * "[Product Name] care instructions"
        
        8. Output Requirements
            - You MUST respond strictly in the JSON schema defined by the ProductSpecification model
            - Provide accurate, specific information (not generic descriptions)
            - If information is not found, use null for optional fields
            - List all sources (URLs) where you found specifications
            - Ensure sizes_available is a list of actual sizes, not descriptions
            - Features should be concise bullet points
        
        9. Quality Guidelines
            - Prioritize official product information from brand/retailer
            - Cross-reference information from multiple sources when possible
            - Be specific: "100% Organic Cotton" not just "Cotton"
            - Include technical details when available
        """),
        output_schema=ProductSpecification,
        db=SqliteDb(session_table="product_specs_agent", db_file="tmp/agents.db"),
        add_datetime_to_context=True,
        use_json_mode=True,
    )
    return agent


def extract_basic_info_from_url(product_url: str) -> Dict:
    """Extract basic product information from URL structure when scraping fails"""
    import re
    from urllib.parse import unquote
    
    # Initialize with defaults
    info = {
        "product_name": "Unknown",
        "brand": "Unknown", 
        "category": "Unknown",
        "color": "Unknown",
        "material": "Unknown"
    }
    
    try:
        # Decode URL
        decoded_url = unquote(product_url)
        
        # Extract brand from domain
        if "shein.com" in product_url.lower():
            info["brand"] = "SHEIN"
        elif "asos.com" in product_url.lower():
            info["brand"] = "ASOS"
        elif "zalando" in product_url.lower():
            info["brand"] = "Zalando"
        elif "zara.com" in product_url.lower():
            info["brand"] = "Zara"
        elif "hm.com" in product_url.lower():
            info["brand"] = "H&M"
        
        # Extract product name from URL path
        # Look for product names in URL segments
        url_parts = decoded_url.split('/')
        for part in url_parts:
            if len(part) > 10 and any(keyword in part.lower() for keyword in 
                ['dress', 'shirt', 'top', 'jacket', 'pants', 'jeans', 'skirt', 'blouse', 'sweater']):
                # Clean up the URL segment to make it readable
                product_name = part.replace('-', ' ').replace('_', ' ')
                # Remove file extensions and parameters
                product_name = re.sub(r'\.(html|php|aspx).*$', '', product_name)
                # Remove product IDs and codes
                product_name = re.sub(r'[p-]\d+.*$', '', product_name)
                # Capitalize words
                product_name = ' '.join(word.capitalize() for word in product_name.split())
                if len(product_name) > 5:  # Only use if meaningful length
                    info["product_name"] = product_name
                    break
        
        # Extract color information from URL
        color_keywords = ['white', 'black', 'red', 'blue', 'green', 'yellow', 'pink', 'purple', 'brown', 'gray', 'grey', 'navy', 'beige', 'cream']
        for color in color_keywords:
            if color in decoded_url.lower():
                info["color"] = color.capitalize()
                break
        
        # Extract category from URL
        category_keywords = {
            'dress': 'Dress', 'shirt': 'Shirt', 'top': 'Top', 'blouse': 'Blouse',
            'jacket': 'Jacket', 'coat': 'Coat', 'pants': 'Pants', 'jeans': 'Jeans',
            'skirt': 'Skirt', 'sweater': 'Sweater', 'hoodie': 'Hoodie'
        }
        for keyword, category in category_keywords.items():
            if keyword in decoded_url.lower():
                info["category"] = category
                break
                
        logger.info(f"Extracted basic info from URL: {info}")
        return info
        
    except Exception as e:
        logger.error(f"Failed to extract info from URL: {e}")
        return info

def extract_specifications(product_url: str, max_retries: int = 3) -> RunOutput:
    payload = dedent(f"""
        product_url: {product_url}
        
        Please extract comprehensive product specifications for this fashion product.
    """)

    agent = product_specs_agent()

    for attempt in range(1, max_retries + 1):
        response = agent.run(input=payload, session_id=str(uuid.uuid4()))
        try:
            validated = ProductSpecification.model_validate(response.content)
            return response
        except Exception as e:
            if attempt < max_retries:
                logger.error(f"Attempt {attempt} failed: {e}. Retrying...")
                continue
            else:
                logger.error(f"All {max_retries} attempts failed. Using URL fallback method.")
                
                # Fallback: Extract basic info from URL
                basic_info = extract_basic_info_from_url(product_url)
                
                fallback_specs = ProductSpecification(
                    product_name=basic_info["product_name"],
                    brand=basic_info["brand"],
                    category=basic_info["category"], 
                    color=basic_info["color"],
                    material=basic_info["material"],
                    sources=[product_url],
                    additional_specs={"extraction_method": "URL parsing fallback"}
                )
                
                # Create a mock response with the fallback data
                response.content = fallback_specs
                return response


if __name__ == "__main__":
    test_url = "https://en.zalando.de/bershka-baby-gifts-black-bej22s0jx-q11.html"
    result = extract_specifications(test_url)
    print("\n" + "="*80)
    print("PRODUCT SPECIFICATIONS")
    print("="*80)
    print(result.content)
