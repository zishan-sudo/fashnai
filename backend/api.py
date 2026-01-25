from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import asyncio
import logging

from PriceAgent import compare_prices, PriceComparisonResult
from ReviewAnalyzerAgent import analyze_reviews, ReviewAnalysis
from ProductSpecsAgent import extract_specifications, ProductSpecification
from api_key_manager import api_key_manager

logger = logging.getLogger(__name__)

app = FastAPI(
    title="FashnAI Fashion Comparison API",
    description="AI-powered fashion product comparison and analysis",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    logger.info(f"FashnAI API starting with {api_key_manager.total_keys} Gemini API key(s)")
    logger.info(f"Rate limit capacity: ~{api_key_manager.total_keys * 5} requests/minute")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SearchRequest(BaseModel):
    product_url: str


class ProductAnalysisResponse(BaseModel):
    prices: PriceComparisonResult
    reviews: ReviewAnalysis
    specifications: ProductSpecification
    status: str = "success"


@app.get("/")
def root():
    return {
        "message": "FashnAI Fashion Comparison API",
        "version": "1.0.0",
        "api_keys": api_key_manager.total_keys,
        "rate_limit": f"~{api_key_manager.total_keys * 5} requests/minute",
        "endpoints": {
            "health": "/health",
            "search": "/api/search (POST)",
            "prices": "/api/prices (POST)",
            "reviews": "/api/reviews (POST)",
            "specs": "/api/specs (POST)"
        }
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy", 
        "service": "FashnAI API",
        "api_keys": api_key_manager.total_keys
    }


@app.post("/api/search", response_model=ProductAnalysisResponse)
async def search_product(request: SearchRequest):
    """
    Comprehensive product analysis - prices, reviews, and specifications
    """
    try:
        logger.info(f"Starting comprehensive analysis for: {request.product_url}")
        
        # Run agents in PARALLEL - each has its own dedicated API key
        logger.info("Running all 3 agents in parallel with dedicated API keys...")
        
        # Create tasks for parallel execution
        price_task = asyncio.create_task(asyncio.to_thread(compare_prices, request.product_url))
        review_task = asyncio.create_task(asyncio.to_thread(analyze_reviews, request.product_url))
        specs_task = asyncio.create_task(asyncio.to_thread(extract_specifications, request.product_url))
        
        # Wait for all to complete
        results = await asyncio.gather(price_task, review_task, specs_task, return_exceptions=True)
        
        # Process price result
        if isinstance(results[0], Exception):
            logger.error(f"PriceAgent failed: {str(results[0])}")
            price_data = PriceComparisonResult(
                original_product_name="Unknown",
                original_product_url=request.product_url,
                product_listings=[],
                search_summary=f"Price comparison unavailable: {str(results[0])}",
                sources_checked=[]
            )
        elif isinstance(results[0].content, str):
            logger.warning(f"PriceAgent returned error: {results[0].content[:200]}")
            price_data = PriceComparisonResult(
                original_product_name="Unknown",
                original_product_url=request.product_url,
                product_listings=[],
                search_summary="Price comparison unavailable due to API error.",
                sources_checked=[]
            )
        else:
            price_data = results[0].content
        
        # Process review result
        if isinstance(results[1], Exception):
            logger.error(f"ReviewAnalyzerAgent failed: {str(results[1])}")
            review_data = ReviewAnalysis(
                overall_rating=0.0,
                total_reviews=0,
                sentiment={"positive": 0, "negative": 0, "neutral": 0},
                pros=[],
                cons=[],
                common_themes=[],
                summary=f"Review analysis unavailable: {str(results[1])}",
                verified_purchase_percentage=0,
                sources_analyzed=[]
            )
        elif isinstance(results[1].content, str):
            logger.warning(f"ReviewAnalyzerAgent returned error: {results[1].content[:200]}")
            review_data = ReviewAnalysis(
                overall_rating=0.0,
                total_reviews=0,
                sentiment={"positive": 0, "negative": 0, "neutral": 0},
                pros=[],
                cons=[],
                common_themes=[],
                summary="Review analysis unavailable due to API error.",
                verified_purchase_percentage=0,
                sources_analyzed=[]
            )
        else:
            review_data = results[1].content
        
        # Process specs result
        if isinstance(results[2], Exception):
            logger.error(f"ProductSpecsAgent failed: {str(results[2])}")
            specs_data = ProductSpecification(
                product_name="Unknown",
                brand="Unknown",
                category="Unknown",
                color="Unknown",
                material="Unknown",
                sizes_available=[],
                care_instructions=None,
                features=[],
                dimensions=None,
                weight=None,
                style_number=None,
                country_of_origin=None,
                sustainability=None,
                fit_type=None,
                additional_specs={},
                sources=[]
            )
        elif isinstance(results[2].content, str):
            logger.warning(f"ProductSpecsAgent returned error: {results[2].content[:200]}")
            specs_data = ProductSpecification(
                product_name="Unknown",
                brand="Unknown",
                category="Unknown",
                color="Unknown",
                material="Unknown",
                sizes_available=[],
                care_instructions=None,
                features=[],
                dimensions=None,
                weight=None,
                style_number=None,
                country_of_origin=None,
                sustainability=None,
                fit_type=None,
                additional_specs={},
                sources=[]
            )
        else:
            specs_data = results[2].content
        
        return ProductAnalysisResponse(
            prices=price_data,
            reviews=review_data,
            specifications=specs_data,
            status="success"
        )
    
    except Exception as e:
        logger.error(f"Error in comprehensive analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/api/prices", response_model=PriceComparisonResult)
async def get_prices(request: SearchRequest):
    """
    Get price comparison across multiple retailers
    """
    try:
        logger.info(f"Fetching prices for: {request.product_url}")
        result = await asyncio.to_thread(compare_prices, request.product_url)
        if isinstance(result.content, str):
            # Agent returned error string instead of model
            return PriceComparisonResult(
                original_product_name="Unknown",
                original_product_url=request.product_url,
                product_listings=[],
                search_summary=f"Error: {result.content}",
                sources_checked=[]
            )
        return result.content
    except Exception as e:
        logger.error(f"Error fetching prices: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Price fetch failed: {str(e)}")


@app.post("/api/reviews", response_model=ReviewAnalysis)
async def get_reviews(request: SearchRequest):
    """
    Get review analysis and sentiment
    """
    try:
        logger.info(f"Analyzing reviews for: {request.product_url}")
        result = await asyncio.to_thread(analyze_reviews, request.product_url)
        if isinstance(result.content, str):
            # Agent returned error string instead of model
            return ReviewAnalysis(
                overall_rating=0.0,
                total_reviews=0,
                sentiment={"positive": 0, "negative": 0, "neutral": 0},
                pros=[],
                cons=[],
                common_themes=[],
                summary=f"Error: {result.content}",
                verified_purchase_percentage=0,
                sources_analyzed=[]
            )
        return result.content
    except Exception as e:
        logger.error(f"Error analyzing reviews: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Review analysis failed: {str(e)}")


@app.post("/api/specs", response_model=ProductSpecification)
async def get_specifications(request: SearchRequest):
    """
    Get product specifications
    """
    try:
        logger.info(f"Extracting specifications for: {request.product_url}")
        result = await asyncio.to_thread(extract_specifications, request.product_url)
        if isinstance(result.content, str):
            # Agent returned error string instead of model
            return ProductSpecification(
                product_name="Unknown",
                brand="Unknown",
                category="Unknown",
                color="Unknown",
                material="Unknown",
                sizes_available=[],
                care_instructions=None,
                features=[],
                dimensions=None,
                weight=None,
                style_number=None,
                country_of_origin=None,
                sustainability=None,
                fit_type=None,
                additional_specs={},
                sources=[]
            )
        return result.content
    except Exception as e:
        logger.error(f"Error extracting specifications: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Specification extraction failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
