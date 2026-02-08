import logging
import uuid
import os
import base64
import io
from textwrap import dedent
from typing import Optional
from agno.agent import Agent, RunOutput
from agno.models.google import Gemini
from agno.db.sqlite import SqliteDb
from agno.tools.crawl4ai import Crawl4aiTools
from agno.media import Image
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from PIL import Image as PILImage
from product_image_extractor import extract_product_images

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(
    "%(asctime)s %(levelname)s [%(name)s] %(message)s"
))
logger.addHandler(handler)

load_dotenv()

# Use Gemini API for virtual try-on (supports vision)
llm = Gemini(
    id='gemini-2.5-flash',
    api_key=os.getenv("GOOGLE_API_KEY_1"),
    vertexai=False
)


class VirtualTryOnResult(BaseModel):
    generated_image_description: str = Field(
        ..., description="Detailed description of how the garment looks on the user")
    fit_analysis: str = Field(
        ..., description="Analysis of how the garment fits the user's body type")
    style_recommendations: list[str] = Field(
        ..., description="Styling recommendations for the outfit")
    confidence_score: float = Field(
        ..., description="Confidence score of the virtual try-on (0.0 to 1.0)")
    size_recommendation: str = Field(
        ..., description="Recommended size based on user's body and garment specifications")
    product_name: str = Field(
        ..., description="Name of the product being tried on")
    warnings: list[str] = Field(
        default_factory=list, description="Any warnings about fit, style, or compatibility")
    generated_image_base64: Optional[str] = Field(
        default=None, description="Base64 encoded generated image of the user wearing the outfit")


def analyze_user_photo(user_image_bytes: bytes) -> str:
    """
    Step 1: Analyze user's photo to understand current clothing, pose, and lighting.
    
    Args:
        user_image_bytes: The user's photo as bytes
        
    Returns:
        Detailed analysis of user's current appearance
    """
    try:
        client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY_1"))
        user_image = PILImage.open(io.BytesIO(user_image_bytes))
        
        analysis_prompt = """Analyze this person's photo and provide detailed information about:

CURRENT CLOTHING ANALYSIS:
- Top: Describe the current top/shirt (type, color, pattern, fit, sleeves, neckline)
- Bottom: Describe pants/bottoms (type, color, fit, length)
- Shoes: Describe footwear (type, color, style)
- Any accessories or outerwear visible

BODY POSITIONING & POSE:
- Arm positioning and pose
- Body angle and stance
- How current clothing fits on their body
- Natural body proportions visible

LIGHTING & PHOTO CONDITIONS:
- Lighting direction and intensity
- Shadow patterns on clothing
- Background type and color
- Overall photo style (studio, casual, etc.)

FABRIC & TEXTURE DETAILS:
- How current fabrics drape and behave
- Visible wrinkles or fabric characteristics
- Material appearance (matte, shiny, textured)

Provide specific, detailed observations that will help with accurate clothing replacement."""

        logger.info("Analyzing user photo with Gemini...")
        
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[analysis_prompt, user_image],
            config=types.GenerateContentConfig(
                response_modalities=['TEXT'],
                temperature=0.3,
                max_output_tokens=2048
            )
        )
        
        analysis = response.candidates[0].content.parts[0].text
        logger.info("Successfully analyzed user photo")
        return analysis
        
    except Exception as e:
        logger.error(f"Failed to analyze user photo: {e}")
        return "Unable to analyze user photo - proceeding with basic replacement"


def generate_tryon_image(
    user_image_bytes: bytes,
    product_specs: Optional[dict] = None,
    product_name: str = "the outfit",
    product_url: Optional[str] = None,
    user_analysis: Optional[str] = None
) -> Optional[str]:
    """
    Generate a virtual try-on image using Gemini's image generation.

    Args:
        user_image_bytes: The user's photo as bytes
        product_specs: Product specifications dict
        product_name: Name of the product

    Returns:
        Base64 encoded generated image, or None if generation fails
    """
    try:
        client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY_1"))

        # Open the user's image
        user_image = PILImage.open(io.BytesIO(user_image_bytes))

        # Create detailed product description from specs or product name
        if product_specs:
            # Enhanced pattern description for accurate replication
            color = product_specs.get('color', 'Unknown')
            product_name = product_specs.get('product_name', product_name)
            features_list = product_specs.get('features', [])
            features_text = '\n  * '.join(features_list) if features_list else 'No specific features listed'
            
            # Check for tie-dye in product name, color, or features
            all_text = f"{product_name} {color} {features_text}".lower()
            pattern_description = ""
            
            if ('tie' in all_text and 'dye' in all_text) or 'tie-dye' in all_text:
                pattern_description = f"""
CRITICAL PATTERN SPECIFICATIONS:
- Pattern Type: Authentic tie-dye (organic, irregular swirl patterns)
- Pattern Style: Natural circular/spiral formations created by fabric bunching and dyeing
- Color Distribution: Irregular organic swirls and bleeds, NOT geometric shapes or stripes
- Pattern Density: Varied throughout garment with natural fade transitions
- Dye Technique: Traditional tie-dye method creating concentric circles and organic flows
- AVOID: Geometric patterns, regular stripes, uniform designs, digital prints
- CRITICAL: This is NOT a striped pattern - it must show organic, hand-dyed swirl effects
                """
            elif 'stripe' in color.lower() or 'striped' in features_text.lower():
                pattern_description = f"""
CRITICAL PATTERN SPECIFICATIONS:
- Pattern Type: Stripes (regular linear patterns)
- Stripe Direction: As specified in product details
- Stripe Width: Consistent width as described
- Color Alternation: Regular alternating pattern
                """
            elif 'floral' in color.lower() or 'flower' in features_text.lower():
                pattern_description = f"""
CRITICAL PATTERN SPECIFICATIONS:
- Pattern Type: Floral print (flower and botanical designs)
- Pattern Distribution: As specified in product details
- Design Elements: Natural flower shapes and botanical motifs
                """
            
            product_description = f"""
EXACT CLOTHING ITEM TO REPLICATE:
- Type: {product_specs.get('category', 'Clothing item')}
- Brand: {product_specs.get('brand', 'Unknown')}
- Product Name: {product_specs.get('product_name', product_name)}
- Color: {color}
- Material: {product_specs.get('material', 'Unknown')}
- Fit Type: {product_specs.get('fit_type', 'Standard fit')}
- Available Sizes: {', '.join(product_specs.get('sizes_available', [])) or 'Various sizes'}

VISUAL SPECIFICATIONS:
- Primary Color: {color} (exact shade and tone)
- Material Properties: {product_specs.get('material', 'Unknown')} (affects drape, texture, and sheen)
- Fit Characteristics: {product_specs.get('fit_type', 'Standard')} fit behavior on body
- Key Design Features:
  * {features_text}
{pattern_description}

CONSTRUCTION DETAILS:
- Care Instructions: {product_specs.get('care_instructions', 'Standard care')}
- Country of Origin: {product_specs.get('country_of_origin', 'Not specified')}
- Style Number: {product_specs.get('style_number', 'Not available')}
            """
        else:
            # Fallback to basic product name description
            product_description = f"""
CLOTHING ITEM TO REPLICATE:
- Product: {product_name}
- Note: Limited product details available - generate based on product name and visible characteristics
- Instruction: Analyze the product name to determine type, style, and likely characteristics
            """

        # Determine what clothing item to replace based on product category
        product_category = product_specs.get('category', 'clothing item').lower() if product_specs else 'clothing item'
        
        # Dynamic replacement instructions based on product type
        if 'top' in product_category or 'shirt' in product_category or 'blouse' in product_category or 'sweater' in product_category:
            current_item = "the current top/shirt the person is wearing"
            positioning = "The new garment should sit exactly where the current top is positioned"
        elif 'dress' in product_category:
            current_item = "any existing dress or top+bottom combination"
            positioning = "The dress should cover the torso and extend to the specified length"
        elif 'pant' in product_category or 'jean' in product_category or 'trouser' in product_category:
            current_item = "the current pants/bottoms the person is wearing"
            positioning = "The new bottoms should sit at the waist and extend to the specified length"
        elif 'shoe' in product_category or 'sneaker' in product_category or 'boot' in product_category:
            current_item = "the current footwear the person is wearing"
            positioning = "The new footwear should be positioned exactly where the current shoes are"
        elif 'jacket' in product_category or 'coat' in product_category or 'blazer' in product_category:
            current_item = "any existing outerwear"
            positioning = "The new outerwear should layer appropriately over existing clothing"
        else:
            current_item = "the relevant existing clothing item"
            positioning = "The new garment should be positioned appropriately on the body"

        # Enhanced prompt with user analysis context
        context_section = ""
        if user_analysis:
            context_section = f"""
USER PHOTO ANALYSIS CONTEXT:
{user_analysis}

Based on the above analysis, ensure the new garment:
- Matches the existing lighting conditions and shadow patterns
- Follows the same fabric draping behavior as observed
- Fits naturally with the person's pose and body positioning
- Replaces only the specified clothing item while preserving everything else
"""

        prompt = f"""PRECISE CLOTHING REPLACEMENT INSTRUCTION: Replace {current_item} with the exact specified garment. DO NOT interpret or modify - paint exactly as described.
{context_section}
CLOTHING DIAGRAM TO PAINT:
{product_description}

EXACT REPLACEMENT TASK:
- REMOVE: {current_item.capitalize()}
- REPLACE WITH: The exact garment as specified in the clothing diagram above
- POSITIONING: {positioning}
- FIT: Match the fit type specified in the product details

STRICT VISUAL REPLICATION REQUIREMENTS:
- Color accuracy: Use the exact colors specified in the product description - NO variations or interpretations
- Pattern/Design: Replicate patterns EXACTLY as described - if tie-dye is mentioned, use organic swirl patterns, NOT stripes or geometric shapes
- Pattern placement: Distribute patterns naturally across the garment as they would appear on the actual product
- Material texture: Show the specified material properties with realistic surface appearance
- Construction details: Include any mentioned seams, stitching, hardware, or decorative elements in exact positions
- Fit behavior: Follow the specified fit type precisely - fitted means form-fitting, loose means relaxed
- Length/Coverage: Match the specified garment length and coverage area exactly
- Scale/Proportion: Ensure all design elements are proportionally correct to the garment size

PHOTO-REALISTIC CONSTRAINTS:
- Maintain exact lighting and shadows from original photo
- Preserve natural fabric draping and wrinkle behavior appropriate to the material
- Keep identical body positioning and natural pose
- Match the studio lighting on the new garment
- Ensure patterns/textures follow the body's natural contours
- Show realistic fabric interaction with body movement

PRESERVE COMPLETELY UNCHANGED:
- Face, hair, expression, skin tone - IDENTICAL
- Body shape, posture, natural positioning - IDENTICAL  
- Any clothing items NOT being replaced - IDENTICAL
- Background, lighting setup, camera angle - IDENTICAL
- Overall photo composition and style - IDENTICAL

CRITICAL INSTRUCTION: Paint ONLY the specified garment from the clothing diagram. Do not add creative interpretations or modifications. The result must look like a professional product photo of this person wearing the exact item described, maintaining complete photographic realism.
"""

        # Try to extract product images if URL is provided
        product_images = []
        if product_url:
            try:
                logger.info(f"Attempting to extract product images from: {product_url}")
                extracted_images = extract_product_images(product_url, max_images=2)
                if extracted_images:
                    product_images = extracted_images
                    logger.info(f"Successfully extracted {len(product_images)} product images")
                else:
                    logger.info("No product images extracted, proceeding with text-only approach")
            except Exception as e:
                logger.warning(f"Product image extraction failed: {e}. Proceeding with text-only approach")

        # Build contents for Gemini - always include prompt and user image
        contents = [prompt, user_image]
        
        # Add product images if successfully extracted
        if product_images:
            contents.extend(product_images)
            logger.info(f"Using {len(product_images)} product reference images + text description")
            # Enhance prompt when we have visual reference
            enhanced_prompt = prompt + "\n\nVISUAL REFERENCE: Use the provided product images as exact reference for colors, patterns, textures, and design details. Replicate the visual appearance shown in the product photos precisely."
            contents[0] = enhanced_prompt
        else:
            logger.info("Using text-only approach for product description")

        logger.info(f"Generating try-on image with Gemini...")

        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash-image",
                contents=contents,
                config=types.GenerateContentConfig(
                    response_modalities=['IMAGE'],
                    temperature=0.1,  # Lower temperature for more consistent clothing replacement
                    top_p=0.8,       # More focused sampling
                    max_output_tokens=8192
                )
            )
        except Exception as gemini_error:
            error_msg = str(gemini_error)
            if "not available in your country" in error_msg or "FAILED_PRECONDITION" in error_msg:
                logger.error(f"Gemini image generation not available in this region: {error_msg}")
                # Return a descriptive error message instead of None
                return "GEOGRAPHIC_RESTRICTION_ERROR"
            else:
                raise gemini_error

        # Extract the generated image
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                # Convert to base64
                image_base64 = base64.b64encode(part.inline_data.data).decode('utf-8')
                logger.info("Successfully generated try-on image")
                return f"data:image/png;base64,{image_base64}"

        logger.warning("No image generated in response")
        return None

    except Exception as e:
        logger.error(f"Failed to generate try-on image: {e}")
        return None


def virtual_tryon_agent() -> Agent:
    agent = Agent(
        name="Virtual Try-On AI Agent",
        model=llm,
        tools=[
            Crawl4aiTools(max_length=10000),
        ],
        tool_call_limit=10,
        description=dedent("""\
        You are an advanced AI fashion stylist and virtual try-on specialist.
        Your role is to analyze fashion products and user characteristics to provide
        realistic virtual try-on insights, fit analysis, and styling recommendations.
        """),
        instructions=dedent("""\
        You will receive a product URL and user characteristics. Your task is to:

        1. Product Analysis Phase
            - Crawl the product URL to extract:
                * Product name, brand, and category
                * Size information and fit type
                * Material and fabric details
                * Design features (cut, style, pattern)
                * Model measurements if shown
                * Available colors and sizes

        2. Virtual Try-On Simulation
            - Based on product details and user characteristics:
                * Describe how the garment would look on the user
                * Consider body type, proportions, and the garment's cut
                * Visualize how the fabric would drape
                * Consider color compatibility with skin tone (if provided)
                * Imagine the overall silhouette and fit

        3. Fit Analysis
            - Analyze how the garment would fit:
                * Consider garment size vs user measurements
                * Note if it would be tight, loose, or just right
                * Identify potential fit issues (e.g., too long, shoulders too wide)
                * Consider the intended fit type (slim, regular, oversized)

        4. Size Recommendation
            - Recommend the best size based on:
                * User's typical size or measurements
                * Brand's sizing standards
                * Garment's fit type
                * User preferences (fitted vs relaxed)

        5. Styling Recommendations
            - Provide 3-5 specific styling suggestions:
                * What to pair it with (e.g., "Pair with high-waisted jeans")
                * Occasion suitability
                * Footwear recommendations
                * Accessory suggestions
                * Color coordination tips

        6. Warnings & Considerations
            - Note any potential issues:
                * "May run small, consider sizing up"
                * "Delicate material, requires careful handling"
                * "Best suited for specific body types"
                * "Color may appear different in person"

        7. Confidence Assessment
            - Assign a confidence score (0.0-1.0) based on:
                * Completeness of product information
                * Clarity of sizing information
                * Availability of model photos and measurements
                * Specificity of user characteristics provided

        8. Output Requirements
            - You MUST respond in the JSON schema defined by VirtualTryOnResult
            - Be specific and realistic in your descriptions
            - Base recommendations on actual product details
            - Provide actionable styling advice
            - Include honest warnings about potential issues
        """),
        output_schema=VirtualTryOnResult,
        db=SqliteDb(session_table="virtual_tryon_agent", db_file="tmp/agents.db"),
        add_datetime_to_context=True,
        use_json_mode=True,
    )
    return agent


def virtual_tryon(
    product_url: str,
    user_size: Optional[str] = None,
    user_height: Optional[str] = None,
    user_body_type: Optional[str] = None,
    user_image_base64: Optional[str] = None,
    product_specs: Optional[dict] = None,
    max_retries: int = 3
) -> RunOutput:
    """
    Perform virtual try-on analysis for a fashion product.

    Args:
        product_url: URL of the fashion product
        user_size: User's typical size (e.g., "M", "L", "32", "8")
        user_height: User's height (e.g., "5'8\"", "173cm")
        user_body_type: User's body type description (e.g., "athletic", "curvy", "slim")
        user_image_base64: Base64 encoded user photo for personalized analysis
        product_specs: Pre-fetched product specifications (to avoid re-crawling)
        max_retries: Maximum number of retry attempts

    Returns:
        RunOutput containing VirtualTryOnResult
    """

    # Build user characteristics string
    user_info = []
    if user_size:
        user_info.append(f"Typical size: {user_size}")
    if user_height:
        user_info.append(f"Height: {user_height}")
    if user_body_type:
        user_info.append(f"Body type: {user_body_type}")

    user_characteristics = "\n".join(user_info) if user_info else "No specific user characteristics provided"

    # Build image analysis instructions
    image_instructions = ""
    if user_image_base64:
        image_instructions = dedent("""

        IMPORTANT: A user photo has been provided as a base64 encoded image.
        Analyze the user's photo to determine:
        - Body shape and proportions
        - Approximate body type (slim, athletic, average, curvy, plus-size)
        - Skin tone (for color recommendations)
        - Current style preferences visible in the photo

        Use these visual observations along with any provided user characteristics
        to give highly personalized fit analysis and styling recommendations.
        """)

    # Build product info section - use cached specs if available
    if product_specs:
        logger.info("Using cached product specifications (skipping crawl)")
        product_info = dedent(f"""
        PRODUCT INFORMATION (pre-fetched, no need to crawl):
        - Product Name: {product_specs.get('product_name', 'Unknown')}
        - Brand: {product_specs.get('brand', 'Unknown')}
        - Category: {product_specs.get('category', 'Unknown')}
        - Color: {product_specs.get('color', 'Unknown')}
        - Material: {product_specs.get('material', 'Unknown')}
        - Available Sizes: {', '.join(product_specs.get('sizes_available', [])) or 'Unknown'}
        - Fit Type: {product_specs.get('fit_type', 'Not specified')}
        - Features: {', '.join(product_specs.get('features', [])) or 'None listed'}
        - Care Instructions: {product_specs.get('care_instructions', 'Not specified')}

        DO NOT crawl the product URL - use the information above for your analysis.
        """)
    else:
        logger.info("No cached specs - agent will crawl the product URL")
        product_info = f"Product URL: {product_url}\n\nPlease crawl this URL to get product details."

    payload = dedent(f"""
        {product_info}

        User Characteristics:
        {user_characteristics}
        {image_instructions}
        Please perform a virtual try-on analysis for this product, providing detailed
        insights about how it would look on a user with these characteristics.
    """)

    agent = virtual_tryon_agent()

    # Build images list if user provided an image
    images = None
    user_image_bytes = None  # Store for image generation
    if user_image_base64:
        try:
            # Clean the base64 string and extract mime type
            mime_type = "image/jpeg"  # default
            raw_base64 = user_image_base64
            if user_image_base64.startswith("data:"):
                # Extract mime type from data URL (e.g., "data:image/png;base64,...")
                header, base64_data = user_image_base64.split(",", 1)
                if "image/png" in header:
                    mime_type = "image/png"
                elif "image/gif" in header:
                    mime_type = "image/gif"
                elif "image/webp" in header:
                    mime_type = "image/webp"
                raw_base64 = base64_data

            # Decode and create Image object
            user_image_bytes = base64.b64decode(raw_base64)
            images = [Image(content=user_image_bytes, mime_type=mime_type)]
            logger.info(f"User image included in analysis (mime_type: {mime_type})")
        except Exception as e:
            logger.warning(f"Failed to decode user image: {e}")
            images = None
            user_image_bytes = None

    for attempt in range(1, max_retries + 1):
        response = agent.run(input=payload, session_id=str(uuid.uuid4()), images=images)
        try:
            result = VirtualTryOnResult.model_validate(response.content)

            # Generate try-on image if user provided a photo
            if user_image_bytes:
                logger.info("Starting multi-step virtual try-on process...")
                
                # Step 1: Analyze user photo first
                user_analysis = analyze_user_photo(user_image_bytes)
                logger.info("User photo analysis completed")
                
                # Step 2: Generate try-on image with analysis context
                generated_image = generate_tryon_image(
                    user_image_bytes=user_image_bytes,
                    product_specs=product_specs,
                    product_name=result.product_name,
                    product_url=product_url,
                    user_analysis=user_analysis
                )
                if generated_image == "GEOGRAPHIC_RESTRICTION_ERROR":
                    result.warnings.append("Image generation is not available in your region. Virtual try-on description provided instead.")
                    result.generated_image_description = f"Virtual try-on simulation: You wearing {result.product_name}. The garment would fit according to the analysis above."
                elif generated_image:
                    result.generated_image_base64 = generated_image
                    # Update the response content with the new result
                    response.content = result

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
    result = virtual_tryon(
        product_url=test_url,
        user_size="M",
        user_height="5'9\"",
        user_body_type="athletic"
    )
    print("\n" + "="*80)
    print("VIRTUAL TRY-ON RESULTS")
    print("="*80)
    print(result.content)
