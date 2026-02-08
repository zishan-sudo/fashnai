# FashnAI - Technical Specification (TypeScript Frontend + Python Backend)

**Version:** 4.1
**Last Updated:** February 2026
**Status:** Implemented & Tested

> **Update (February 2026):** Added **Virtual Try-On Agent** with AI-powered image generation using Gemini 3.0 Flash Image. The agent provides personalized fit analysis, size recommendations, and styling suggestions based on user characteristics and product specifications. New endpoint: `POST /api/virtual-tryon`. See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed implementation.

---

## 1. System Architecture

### 1.1 High-Level Flow

```
User Input (Product URL)
    ↓
[Next.js 14 Frontend - TypeScript]
    ↓ POST /api/search
[FastAPI Backend - Python]
    ↓ Parallel Execution
[Agno AI Agents - Gemini 3.0 Flash]
    ├─ PriceAgent (Fashion price comparison)
    ├─ ReviewAnalyzerAgent (Sentiment + pros/cons)
    └─ ProductSpecsAgent (Materials + sizes)
    ↓
[Web Scraping Tools]
    ├─ SerperTools (Google Search)
    └─ Crawl4aiTools (Web crawling)
    ↓
[Fashion E-commerce Websites]
    ↓
[Aggregated Results]
    ↓
[Frontend Display - Tabbed UI]
```

### 1.2 Backend Stack

- **Runtime:** Python 3.13
- **Framework:** FastAPI 0.115+
- **AI Framework:** Agno 2.4+
- **LLM Model:** Google Gemini 3.0 Flash
- **Web Search:** SerperTools (Serper API)
- **Web Scraping:** Crawl4aiTools (Playwright + Chromium)
- **Database:** SQLite (via Agno for session management)
- **HTTP Client:** httpx (async)
- **Package Manager:** uv (fast Python package manager)
- **Environment:** python-dotenv

### 1.3 Frontend Stack

- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript 5
- **UI Library:** React 18
- **Styling:** Tailwind CSS 3.4
- **Icons:** Lucide React
- **HTTP Client:** Axios
- **Type Definitions:** @types/react, @types/node
- **Package Manager:** npm

---

## 2. Core Module: LLM Web Scraper Agent

### 2.1 Agent Design Pattern

Each agent follows this pattern:

```python
class RetailerAgent:
    def __init__(self, retailer_name: str):
        self.retailer = retailer_name
        self.llm_client = Anthropic()  # or OpenAI
    
    async def fetch_product_page(self, product_name: str) -> str:
        # 1. Search for product on retailer
        # 2. Fetch HTML
        # 3. Return HTML
    
    async def extract_data(self, html: str) -> dict:
        # 1. Create prompt with HTML
        # 2. Call LLM
        # 3. Parse JSON response
        # 4. Validate data
        # 5. Return structured data
    
    async def scrape(self, product_name: str) -> dict:
        html = await self.fetch_product_page(product_name)
        return await self.extract_data(html)
```

### 2.2 System Prompt Template

```
You are a web scraper for {RETAILER}. 

Extract the following from the product page HTML:
1. Product Price (in INR, integer only)
2. Availability Status (enum: IN_STOCK, OUT_OF_STOCK, LIMITED_STOCK)
3. Star Rating (0-5, float)
4. Review Count (integer)
5. Key Features (list of 3-5 strings)
6. Product URL (full path)

If any field is missing, use null.

Return ONLY valid JSON:
{
  "price": 2499,
  "availability": "IN_STOCK",
  "rating": 4.5,
  "review_count": 1234,
  "features": ["Feature 1", "Feature 2"],
  "url": "https://..."
}
```

### 2.3 Retailers Configuration

```python
RETAILERS_CONFIG = {
    "amazon": {
        "base_url": "https://www.amazon.in",
        "search_endpoint": "/s",
        "search_param": "k",
        "timeout": 30,
        "retry_count": 3
    },
    "flipkart": {
        "base_url": "https://www.flipkart.com",
        "search_endpoint": "/search",
        "search_param": "q",
        "timeout": 30,
        "retry_count": 3
    },
    # ... more retailers
}
```

### 2.4 Error Handling

```python
class ScraperException(Exception):
    """Base exception for scraper"""

class RetryableError(ScraperException):
    """Retriable errors (timeout, rate limit)"""

class FatalError(ScraperException):
    """Non-retriable errors (invalid HTML, LLM failure)"""

async def scrape_with_retry(agent, product_name, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await agent.scrape(product_name)
        except RetryableError:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # exponential backoff
                await asyncio.sleep(wait_time)
            else:
                raise
        except FatalError:
            return None  # Return empty result
```

---

## 3. API Specification

### 3.1 Search Endpoint

**Endpoint:** `POST /api/search`

**Request Body:**
```json
{
  "product_name": "Woodland leather shoes",
  "max_results": 10,
  "price_range": {
    "min": 1000,
    "max": 10000
  }
}
```

**Response (200 OK):**
```json
{
  "product_name": "Woodland leather shoes",
  "status": "success",
  "results": [
    {
      "retailer": "FLIPKART",
      "price": 2499,
      "availability": "IN_STOCK",
      "rating": 4.5,
      "review_count": 1234,
      "features": ["Genuine Leather", "Comfortable Sole"],
      "url": "https://flipkart.com/...",
      "affiliate_link": "https://affiliate.com/..."
    },
    {
      "retailer": "AMAZON",
      "price": 2599,
      "availability": "IN_STOCK",
      "rating": 4.3,
      "review_count": 567,
      "features": ["Waterproof", "Long-lasting"],
      "url": "https://amazon.in/...",
      "affiliate_link": "https://affiliate.com/..."
    }
  ],
  "analysis": {
    "cheapest_option": "FLIPKART",
    "best_rated": "FLIPKART",
    "average_price": 2549,
    "price_range": [2499, 2599],
    "in_stock_count": 5
  },
  "execution_time_ms": 8500
}
```

**Error Response (500):**
```json
{
  "status": "error",
  "message": "Failed to scrape retailers",
  "details": "LLM API timeout"
}
```

### 3.2 Product Details Endpoint

**Endpoint:** `POST /api/product/analyze`

**Request Body:**
```json
{
  "product_url": "https://amazon.in/dp/...",
  "retailer": "AMAZON"
}
```

**Response:**
```json
{
  "product_name": "Woodland Shoes",
  "description": "Premium leather shoes...",
  "reviews_summary": {
    "sentiment": {
      "positive": 78,
      "neutral": 15,
      "negative": 7
    },
    "pros": [
      "Very comfortable",
      "Great quality",
      "Good value"
    ],
    "cons": [
      "Takes time to break in",
      "Limited color options"
    ],
    "summary": "Highly recommended for comfort..."
  }
}
```

### 3.3 Cache Endpoint

**Endpoint:** `GET /api/cache/stats`

**Response:**
```json
{
  "total_searches": 1234,
  "cache_size_mb": 45.6,
  "cache_hit_rate": 0.82,
  "cached_products": 567
}
```

---

## 4. Database Schema (Optional)

If persistence needed:

```sql
-- Products cache
CREATE TABLE products (
  id UUID PRIMARY KEY,
  name VARCHAR NOT NULL,
  hash VARCHAR UNIQUE,  -- hash(name)
  data JSONB,
  created_at TIMESTAMP,
  ttl_hours INT DEFAULT 24
);

-- Search history
CREATE TABLE searches (
  id UUID PRIMARY KEY,
  query VARCHAR NOT NULL,
  results_count INT,
  execution_time_ms INT,
  status VARCHAR,
  created_at TIMESTAMP
);

-- Retailer stats
CREATE TABLE retailer_stats (
  id UUID PRIMARY KEY,
  retailer VARCHAR NOT NULL,
  success_count INT,
  failure_count INT,
  avg_response_time_ms INT,
  last_updated TIMESTAMP
);
```

---

## 5. LLM Configuration

### 5.1 Anthropic (Claude)

```python
from anthropic import Anthropic

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": prompt}
    ]
)
```

### 5.2 OpenAI (GPT-4)

```python
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model="gpt-4",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": prompt}
    ]
)
```

### 5.3 Fallback Logic

```python
async def call_llm_with_fallback(prompt: str):
    try:
        # Try Claude first (cheaper, faster)
        result = await call_claude(prompt)
        return result
    except Exception as e:
        logger.warning(f"Claude failed: {e}, falling back to GPT-4")
        try:
            result = await call_gpt4(prompt)
            return result
        except Exception as e:
            logger.error(f"Both LLM calls failed: {e}")
            raise LLMFailureError("Unable to extract data")
```

---

## 6. Caching Strategy

### 6.1 In-Memory Cache (Development)

```python
from functools import lru_cache
import hashlib

class SearchCache:
    def __init__(self, max_size=1000, ttl_hours=24):
        self.cache = {}
        self.max_size = max_size
        self.ttl_hours = ttl_hours
    
    def get_key(self, product_name):
        return hashlib.md5(product_name.encode()).hexdigest()
    
    def get(self, product_name):
        key = self.get_key(product_name)
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl_hours * 3600:
                return data
        return None
    
    def set(self, product_name, data):
        if len(self.cache) >= self.max_size:
            # Remove oldest entry
            oldest_key = min(self.cache.keys(), 
                           key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]
        
        key = self.get_key(product_name)
        self.cache[key] = (data, time.time())
```

### 6.2 Redis Cache (Production)

```python
import redis
import json

class RedisCache:
    def __init__(self, redis_url="redis://localhost:6379"):
        self.redis_client = redis.from_url(redis_url)
    
    def get(self, product_name):
        result = self.redis_client.get(f"search:{product_name}")
        return json.loads(result) if result else None
    
    def set(self, product_name, data, ttl_hours=24):
        key = f"search:{product_name}"
        self.redis_client.setex(
            key,
            ttl_hours * 3600,
            json.dumps(data)
        )
```

---

## 7. Deployment Configuration

### 7.1 Python Backend (.env)

```env
# LLM APIs
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=false
LOG_LEVEL=INFO

# Cache
CACHE_TYPE=redis  # or 'memory'
REDIS_URL=redis://localhost:6379

# CORS
FRONTEND_URL=https://flash-search-xxxxx.netlify.app
```

### 7.2 Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "main:app", "--workers", "4", "--timeout", "120"]
```

### 7.3 Deploy Commands

**Railway:**
```bash
# Install Railway CLI
npm i -g @railway/cli

# Deploy
railway up

# View logs
railway logs
```

**Render:**
```bash
# Create service on render.com
# Push to GitHub
# Auto-deploys on git push
```

---

## 8. Monitoring & Logging

### 8.1 Logging Setup

```python
import logging
from pythonjsonlogger import jsonlogger

logger = logging.getLogger(__name__)

logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

logger.info("Search started", extra={
    "product_name": "shoes",
    "retailers": 6,
    "timestamp": datetime.now().isoformat()
})
```

### 8.2 Performance Metrics

```python
from prometheus_client import Counter, Histogram

search_counter = Counter('searches_total', 'Total searches')
search_duration = Histogram('search_duration_seconds', 'Search duration')

@search_duration.time()
async def search_product(product_name):
    search_counter.inc()
    # ... search logic
```

---

## 9. Testing Strategy

### 9.1 Unit Tests

```python
# test_web_scraper.py
import pytest
from agents.web_scraper import WebScraperAgent

@pytest.mark.asyncio
async def test_extract_amazon_price():
    agent = WebScraperAgent("amazon")
    html = open("tests/fixtures/amazon_product.html").read()
    result = await agent.extract_data(html)
    
    assert result["price"] == 2499
    assert result["availability"] == "IN_STOCK"
    assert result["rating"] == 4.5
```

### 9.2 Mock LLM Response

```python
@pytest.fixture
def mock_llm_response():
    return {
        "price": 2499,
        "availability": "IN_STOCK",
        "rating": 4.5,
        "review_count": 1234,
        "features": ["Feature 1", "Feature 2"]
    }
```

### 9.3 Integration Tests

```python
@pytest.mark.asyncio
async def test_full_search_flow():
    client = TestClient(app)
    response = client.post("/api/search", json={
        "product_name": "shoes"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) > 0
```

---

## 10. Performance Considerations

### 10.1 Parallel Requests

```python
async def search_all_retailers(product_name):
    # Create tasks for all retailers
    tasks = [
        agent.scrape(product_name)
        for agent in retailer_agents
    ]
    
    # Execute in parallel with timeout
    results = await asyncio.wait_for(
        asyncio.gather(*tasks, return_exceptions=True),
        timeout=30.0
    )
    
    return [r for r in results if not isinstance(r, Exception)]
```

### 10.2 Response Times

| Component | Target (ms) | Notes |
|-----------|-----------|-------|
| Fetch HTML | 2000 | Per retailer |
| LLM call | 3000 | Per retailer |
| Total (parallel) | 8000 | 6 retailers in parallel |
| Frontend render | 1000 | With results |

### 10.3 Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/search")
@limiter.limit("10/minute")
async def search_product(request: SearchRequest):
    pass
```

---

## 11. Security Considerations

### 11.1 API Key Management

```python
# Use environment variables, never hardcode
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY not set")
```

### 11.2 Input Validation

```python
from pydantic import BaseModel, validator

class SearchRequest(BaseModel):
    product_name: str
    
    @validator('product_name')
    def product_name_valid(cls, v):
        if not v or len(v) > 200:
            raise ValueError('Invalid product name')
        return v.strip()
```

### 11.3 Rate Limiting

```python
# Per IP: 100 requests/hour
# Per product: 1 request/5 seconds
```

---

## 12. Success Criteria

✅ **MVP (Mandatory):**
- Backend scrapes 3+ retailers
- Frontend displays prices
- Deploy locally working

✅ **Good (Competitive):**
- All 6 retailers working
- Reviews analysis working
- <10s response time
- Deployed to production

✅ **Excellent (Impressive):**
- All above + caching
- Monitoring/logging
- A/B testing different LLM models
- Affiliate link tracking

---

**Implementation Timeline: 24-48 hours**
