import logging
import uuid
import os
from textwrap import dedent
from typing import List
from agno.agent import Agent, RunOutput
from agno.models.google import Gemini
from agno.tools.serper import SerperTools
from agno.tools.crawl4ai import Crawl4aiTools
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from database import db

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(
    "%(asctime)s %(levelname)s [%(name)s] %(message)s"
))
logger.addHandler(handler)

load_dotenv()

# Use paid Gemini API key for all agents with Agno database
llm = Gemini(
    id='gemini-2.0-flash',
    api_key=os.getenv("GOOGLE_API_KEY"),
    vertexai=False
)

agent = Agent(
    model=llm,
    tools=[SerperTools(), Crawl4aiTools()],
    db=db,
    enable_user_memories=True,
    show_tool_calls=True,
    markdown=True
)


class ProductListing(BaseModel):
    website_name: str = Field(
        ..., description="Name of the fashion e-commerce website (e.g., ASOS, Zara, H&M, Nordstrom, etc.)")
    product_url: str = Field(
        ..., description="Direct URL to the product page on this website")
    price: str = Field(
        ..., description="Current price of the product including currency symbol (e.g., $49.99, €45.00)")
    availability: str = Field(
        ..., description="Product availability status (e.g., In Stock, Out of Stock, Limited Stock)")
    seller_info: str = Field(
        default="Not specified", description="Seller or vendor information if available")


class PriceComparisonResult(BaseModel):
    original_product_name: str = Field(
        ..., description="Name/title of the fashion product (apparel or shoes) being searched")
    original_product_url: str = Field(
        ..., description="The original product URL provided as input")
    product_listings: List[ProductListing] = Field(
        ..., description="List of product listings found across different e-commerce websites with their prices")
    search_summary: str = Field(
        ..., description="Brief summary of the search results and price range found")
    sources_checked: List[str] = Field(
        ..., description="List of all URLs checked during the research process")


def price_agent() -> Agent:
    agent = Agent(
        name="Fashion Price Comparison Agent",
        model=llm,
        tools=[
            SerperTools(),
            Crawl4aiTools(max_length=12000),
        ],
        tool_call_limit=15,
        description=dedent("""\
        You are an intelligent fashion price comparison agent specialized in apparel and footwear. 
        Your job is to find the same fashion product (clothing, shoes, accessories) across multiple 
        fashion e-commerce websites and extract their prices, availability, sizes, and seller information 
        to help users make informed purchasing decisions.
        """),
        instructions=dedent("""\
        You will receive a product URL from a fashion e-commerce website. Your task is to:
        
        1. Product Identification Phase
            - Crawl the provided product URL to extract:
                * Product name/title
                * Brand name
                * Style number, SKU, or product code (if available)
                * Product category (e.g., dress, jeans, sneakers, boots, jacket, etc.)
                * Color/colorway
                * Material/fabric composition
                * Key design features or identifiers
                * Current price on the original website
                * Available sizes
            - Identify unique product identifiers (style number, SKU, UPC, EAN, etc.)
        
        2. Search Phase
            - IMPORTANT: Search for information about the place using the search_google function.Use the product name, brand, style number, and category to search for the same fashion item on other fashion platforms
           
            - IMPORTANT: Use the web_crawler function to extract information from various websites on the search results, the overall analysis MUST contain evidence that was fetched using the crawler.
            - IMPORTANT: Crawl on all the weblinks on the search results for information
            - Use search_google to find product listings with queries like:
                * "[Brand] [Style Number] [Product Name] buy"
                * "[Brand] [Product Name] [Color] price"
                * "[Product Name] [Brand] fashion"
                * "[Style Number] [Brand]"
        
        3. Verification Phase
            - For each potential match found, crawl the product page to verify:
                * It is the EXACT same fashion item (same brand, style, color, design)
                * Extract the current price (including currency)
                * Check availability status and size availability
                * Note the seller/retailer information
            - Only include listings that are confirmed to be the same product
            - Exclude listings that are:
                * Different colors or styles
                * Different seasons/collections (unless explicitly the same)
                * Used/vintage items (unless the original is also used/vintage)
                * From unreliable or suspicious websites
                * Counterfeit or replica items
        
        4. Price Extraction Guidelines
            - Extract the final price shown to customers (after any automatic discounts)
            - Include currency symbol with the price
            - Note if there are shipping costs mentioned
            - Check for any special offers or promotions
        
        5. Output Requirements
            - You MUST respond strictly in the JSON schema defined by the PriceComparisonResult model
            - Include the original product information and URL
            - List ALL verified product listings found across different websites
            - Provide a brief search summary including:
                * Number of websites checked
                * Price range found (lowest to highest)
                * Any notable price differences or deals
            - Include all URLs you actively used in the sources_checked field
            - If you cannot find the product on other websites, still return the original listing
              and explain in the search_summary why no other listings were found
        """),
        output_schema=PriceComparisonResult,
        db=SqliteDb(session_table="price_comparison_agent", db_file="tmp/agents.db"),
        add_datetime_to_context=True,
        use_json_mode=True,
    )
    return agent


def compare_prices(product_url: str, max_retries: int = 3) -> RunOutput:
    payload = dedent(f"""
        product_url: {product_url}
        
        Please find this product on other e-commerce websites and compare prices.
    """)

    agent = price_agent()

    for attempt in range(1, max_retries + 1):
        response = agent.run(input=payload, session_id=str(uuid.uuid4()))
        try:
            _ = PriceComparisonResult.model_validate(response.content)
            return response
        except Exception as e:
            if attempt < max_retries:
                logger.error(f"Attempt {attempt} failed: {e}. Retrying...")
                continue
            else:
                logger.error(f"All {max_retries} attempts failed. Returning last response.")
                return response


if __name__ == "__main__":
    test_url = "https://en.zalando.de/bershka-baby-gifts-black-bej22s0jx-q11.html"
    result = compare_prices(test_url)
    print("\n" + "="*80)
    print("PRICE COMPARISON RESULTS")
    print("="*80)
    print(result.content)
