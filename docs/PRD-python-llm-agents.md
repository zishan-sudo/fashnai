# Flash.co Clone - Hackathon Edition (Python + LLM Agents)

**Version:** 3.0 (Python + Agent-Based Web Scraping)
**Stack:** Python FastAPI + LLM Web Parsers + Next.js Frontend
**Duration:** 24-48 hours
**Scope:** MVP with AI agents for web scraping

> **Update (February 2026):** This is the original PRD. The project has since been rebranded as **FashnAI** and enhanced with a **Virtual Try-On agent** that provides AI-powered fit analysis, size recommendations, and styling suggestions using Gemini 2.5 Flash Image. See [ARCHITECTURE.md](ARCHITECTURE.md) for current system design.

---

## 1. Executive Summary

Build a **product comparison aggregator** using:
- **Backend:** Python FastAPI (LLM-based web scraping agents)
- **Frontend:** Next.js (React + Tailwind)
- **Web Scraping:** LLM agents parse efashion retailer websites
- **Deployment:** Simple Python server + Netlify frontend

**Key Innovation:** Use Gemini as intelligent web parser - extracts prices, reviews, availability from unstructured HTML naturally.

---

## 2. Problem & Solution

### Problem
Users waste time visiting 6 retailers to compare prices and read reviews.

### Solution
1. User searches for product
2. Backend LLM agent searches web and scrapes websites to get prices and availability
3. Backend LLM agent analyzes reviews (sentiment, pros/cons)
4. Frontend displays curated results
5. User clicks affiliate link to purchase

---

## 3. Architecture

```
┌─────────────────────────────┐
│  Next.js 14 Frontend        │
│  (TypeScript + React 18)    │
│  Port: 3000                 │
│                             │
│  ├─ Home/Search Page        │
│  └─ Product Details Page    │
└────────┬────────────────────┘
         │ REST API (HTTP)
         │ POST /api/search
         │ POST /api/prices
         │ POST /api/reviews
         │ POST /api/specs
         ↓
┌─────────────────────────────┐
│  Python FastAPI Backend     │
│  Port: 8000                 │
│                             │
│  ├─ API Routes              │
│  ├─ CORS Middleware         │
│  └─ Async Task Orchestration│
└────────┬────────────────────┘
         │
         ↓
┌─────────────────────────────┐
│  Agno AI Agents             │
│  (Gemini 2.5 Flash)         │
│                             │
│  ├─ PriceAgent              │
│  │   └─ Fashion retailers   │
│  │       price comparison   │
│  │                          │
│  ├─ ReviewAnalyzerAgent     │
│  │   └─ Sentiment analysis  │
│  │       pros/cons extraction│
│  │                          │
│  └─ ProductSpecsAgent       │
│      └─ Material, sizes,    │
│          care instructions  │
└────────┬────────────────────┘
         │
         ↓
┌─────────────────────────────┐
│  Web Scraping Tools         │
│                             │
│  ├─ SerperTools (Search)    │
│  └─ Crawl4aiTools (Scrape)  │
└────────┬────────────────────┘
         │
         ↓
┌─────────────────────────────┐
│  Fashion E-commerce Sites   │
│                             │
│  ├─ Zalando, ASOS, Zara     │
│  ├─ H&M, Nordstrom, Macy's  │
│  └─ Other fashion retailers │
└─────────────────────────────┘
```

---

## 4. Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| **Frontend** | Next.js 14 + TypeScript + React 18 + Tailwind CSS | Type-safe UI, SEO, modern design |
| **Backend** | Python 3.13 + FastAPI | Fast async API, auto docs |
| **AI Framework** | Agno 2.4+ | Multi-agent orchestration |
| **LLM Model** | Google Gemini 2.5 Flash | Fast, intelligent parsing |
| **Web Search** | SerperTools (Serper API) | Real-time search results |
| **Web Scraping** | Crawl4aiTools (Playwright) | JavaScript-enabled scraping |
| **Database** | SQLite (via Agno) | Session/agent state storage |
| **HTTP Client** | httpx + axios | Async requests (backend + frontend) |
| **Package Manager** | uv (backend) + npm (frontend) | Fast, reliable dependencies |
| **Deployment** | Local/Cloud Python server | Flexible hosting |

---

## 5. Core Feature: LLM Web Scraper Agent

### How It Works

**Traditional scraping (brittle):**
```python
price = soup.select('.price-tag')[0].text
# ❌ Breaks if HTML changes
```

**LLM agent (intelligent):**
```python
html = fetch_website("https://amazon.in/product/xyz")
agent = WebScraperAgent()
result = agent.extract_product_info(html)
# Returns: {price: 2499, availability: "In Stock", reviews: 4.5}
# ✅ Works even if HTML structure changes
```

### Agent System Prompt

```python
SYSTEM_PROMPT = """
You are a web scraper agent. Extract product information from HTML.

Extract:
1. Price (in INR, remove special chars)
2. Availability (In Stock / Out of Stock / Limited)
3. Rating (0-5 stars)
4. Review count
5. Key features (3-5 bullet points)

Return JSON:
{
  "price": 2499,
  "availability": "In Stock",
  "rating": 4.5,
  "review_count": 1234,
  "features": ["...", "..."]
}
"""
```

---

## 6. Backend Architecture (Python)

### Project Structure

```
backend/
├── main.py                      # FastAPI app
├── agents/
│   ├── web_scraper.py          # LLM web scraper
│   ├── review_analyzer.py      # Review analysis
│   └── retailer_agents.py      # Per-retailer logic
├── api/
│   ├── routes.py               # API endpoints
│   └── schemas.py              # Pydantic models
├── utils/
│   ├── http_client.py          # Async HTTP
│   ├── cache.py                # Caching
│   └── logger.py               # Logging
├── config.py                   # Settings
├── requirements.txt            # Dependencies
└── .env                        # Secrets
```

---

## 7. Key Python Files

### `requirements.txt`

```
fastapi==0.104.1
uvicorn==0.24.0
httpx==0.25.1
anthropic==0.7.0
openai==1.3.0
pydantic==2.5.0
python-dotenv==1.0.0
redis==5.0.0
```

### `main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router

app = FastAPI(title="Flash Clone Backend")

# CORS for Netlify frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://flash-search-xxxxx.netlify.app", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### `agents/web_scraper.py`

```python
import httpx
from anthropic import Anthropic
import json
import asyncio

class WebScraperAgent:
    def __init__(self):
        self.client = Anthropic()
        self.model = "claude-3-5-sonnet-20241022"  # or use gpt-4
        
    async def scrape_retailer(self, product_name: str, retailer: str) -> dict:
        """Scrape product info from retailer using LLM agent"""
        
        # Step 1: Find product URL
        search_url = f"https://www.{retailer}/s?q={product_name}"
        
        # Step 2: Fetch HTML
        async with httpx.AsyncClient() as client:
            response = await client.get(search_url, headers={
                "User-Agent": "Mozilla/5.0..."
            })
            html = response.text[:50000]  # First 50KB
        
        # Step 3: Use LLM agent to extract data
        prompt = f"""
Extract product information from this HTML:

{html}

Return JSON with:
- price (INR number)
- availability (In Stock / Out of Stock)
- rating (0-5)
- review_count (number)
"""
        
        message = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Step 4: Parse response
        response_text = message.content[0].text
        result = json.loads(response_text)
        
        return {
            "retailer": retailer.upper(),
            "price": result["price"],
            "availability": result["availability"],
            "rating": result.get("rating", 0),
            "review_count": result.get("review_count", 0),
            "url": search_url
        }
    
    async def scrape_all_retailers(self, product_name: str, retailers: list) -> list:
        """Scrape all retailers in parallel"""
        tasks = [
            self.scrape_retailer(product_name, retailer)
            for retailer in retailers
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [r for r in results if not isinstance(r, Exception)]
```

### `agents/review_analyzer.py`

```python
from anthropic import Anthropic
import json

class ReviewAnalyzerAgent:
    def __init__(self):
        self.client = Anthropic()
        self.model = "claude-3-5-sonnet-20241022"
    
    async def analyze_reviews(self, product_name: str, reviews_text: str) -> dict:
        """Analyze reviews using LLM agent"""
        
        prompt = f"""
Analyze these product reviews for: {product_name}

Reviews:
{reviews_text}

Extract and return JSON:
{{
  "sentiment": {{"positive": 0-100, "negative": 0-100, "neutral": 0-100}},
  "pros": ["pro1", "pro2", "pro3"],
  "cons": ["con1", "con2", "con3"],
  "summary": "2-3 sentence summary"
}}
"""
        
        message = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = message.content[0].text
        return json.loads(response_text)
```

### `api/routes.py`

```python
from fastapi import APIRouter, HTTPException
from api.schemas import SearchRequest, SearchResponse
from agents.web_scraper import WebScraperAgent
from agents.review_analyzer import ReviewAnalyzerAgent
import asyncio

router = APIRouter()
scraper_agent = WebScraperAgent()
review_agent = ReviewAnalyzerAgent()

RETAILERS = ["amazon.in", "flipkart.com", "myntra.com", "nykaa.com", "tatacliq.com"]

@router.post("/search")
async def search_product(request: SearchRequest) -> SearchResponse:
    """Search for product across retailers"""
    
    try:
        # Step 1: Scrape prices from all retailers
        prices = await scraper_agent.scrape_all_retailers(
            request.product_name,
            RETAILERS
        )
        
        # Step 2: Fetch and analyze reviews
        # (In real world, would search and fetch reviews separately)
        reviews_text = f"Product reviews for {request.product_name}..."
        reviews = await review_agent.analyze_reviews(
            request.product_name,
            reviews_text
        )
        
        # Step 3: Sort by price
        prices.sort(key=lambda x: x["price"])
        
        return SearchResponse(
            product_name=request.product_name,
            prices=prices,
            reviews=reviews,
            status="success"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### `api/schemas.py`

```python
from pydantic import BaseModel
from typing import List

class SearchRequest(BaseModel):
    product_name: str

class PriceResult(BaseModel):
    retailer: str
    price: int
    availability: str
    rating: float
    review_count: int
    url: str

class ReviewAnalysis(BaseModel):
    sentiment: dict  # {positive, negative, neutral}
    pros: List[str]
    cons: List[str]
    summary: str

class SearchResponse(BaseModel):
    product_name: str
    prices: List[PriceResult]
    reviews: ReviewAnalysis
    status: str
```

---

## 8. Frontend (Same as Before)

Next.js with React + Tailwind (unchanged).

Just update API endpoint:

```typescript
// From: localhost:3000/api/search
// To: localhost:8000/api/search
const response = await fetch('http://localhost:8000/api/search', {
  method: 'POST',
  body: JSON.stringify({ product_name })
})
```

---

## 9. Windsurf Rules Files

Create `.windsurf/rules` directory with:

### `.windsurf/rules/python-backend.md`

```markdown
# Python Backend Rules

## Code Style
- Use type hints for all functions
- Follow PEP 8 style guide
- Max line length: 100 characters
- Use async/await for I/O operations

## Project Structure
```
flask-backend/
├── agents/          # LLM agent modules
├── api/             # FastAPI routes
├── utils/           # Helper functions
└── config.py        # Configuration
```

## LLM Agent Pattern
Every agent should:
1. Take raw input (HTML, text, etc.)
2. Create prompt
3. Call LLM API
4. Parse JSON response
5. Return structured data

## Testing
- Test agents with sample HTML
- Mock LLM responses for unit tests
- Integration test: FastAPI → Agent → External API

## Dependencies
- fastapi: Web framework
- httpx: Async HTTP client
- anthropic: Claude API
- openai: GPT-4 API
```

### `.windsurf/rules/llm-agents.md`

```markdown
# LLM Web Scraper Agents Rules

## Agent Architecture
Each retailer gets one agent:
- Amazon agent: Understands Amazon HTML
- Flipkart agent: Understands Flipkart HTML
- etc.

## Prompting Strategy
1. **Clear task**: "Extract product price from HTML"
2. **Context**: Provide sample HTML if possible
3. **Format**: Specify exact JSON output
4. **Fallback**: What to return if data not found

## Parsing HTML
- Use BeautifulSoup for initial cleanup
- Pass to LLM for intelligent extraction
- LLM handles variations in HTML structure

## Error Handling
- If LLM fails: Return None
- If HTTP fails: Retry 3 times
- If all retailers fail: Return empty list

## Performance
- Parallel requests: asyncio.gather()
- Timeout per retailer: 30 seconds
- Cache responses: Redis (optional)

## Retry Logic
```python
async def retry(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
```
```

### `.windsurf/rules/next-frontend.md`

```markdown
# Next.js Frontend Rules

## Component Structure
- One component per file
- Use functional components + hooks
- Props typed with TypeScript

## API Integration
- Backend URL: http://localhost:8000/api
- Endpoints: POST /search, GET /health
- Handle loading, error, success states

## Styling
- Tailwind CSS only
- No CSS modules
- Responsive: mobile-first

## Performance
- Use React.memo for heavy components
- Debounce search input
- Lazy load images

## Error Handling
- Show user-friendly error messages
- Log errors to console
- Fallback UI if API unavailable
```

### `.windsurf/rules/testing.md`

```markdown
# Testing Rules

## Unit Tests (Python)
```bash
pytest agents/test_web_scraper.py
pytest api/test_routes.py
```

## Integration Tests
- Test full search flow
- Mock external APIs
- Verify JSON responses

## E2E Tests (Frontend)
```bash
npm run test:e2e
```

## Test Data
- Keep sample HTML in `tests/fixtures/`
- Use real API responses for mocking
- Update fixtures when HTML changes
```

### `.windsurf/workspace.json`

```json
{
  "folders": [
    {
      "path": ".",
      "name": "Flash Clone"
    }
  ],
  "settings": {
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "[python]": {
      "editor.defaultFormatter": "ms-python.python",
      "editor.formatOnSave": true
    },
    "[typescript]": {
      "editor.defaultFormatter": "esbenp.prettier-vscode",
      "editor.formatOnSave": true
    }
  },
  "extensions": {
    "recommendations": [
      "ms-python.python",
      "ms-python.vscode-pylance",
      "esbenp.prettier-vscode",
      "bradlc.vscode-tailwindcss",
      "charliermarsh.ruff"
    ]
  }
}
```

---

## 10. Development Workflow

### Terminal 1: Python Backend
```bash
cd flash-backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
# Running on http://localhost:8000
```

### Terminal 2: Next.js Frontend
```bash
cd flash-frontend
npm install
npm run dev
# Running on http://localhost:3000
```

### Terminal 3: Testing/Debugging
```bash
# Test agent
python -c "from agents.web_scraper import WebScraperAgent; ..."

# Check logs
tail -f logs/app.log

# API health check
curl http://localhost:8000/health
```

---

## 11. Deployment

### Backend (Python Server)
```bash
# Deploy to Railway, Render, or similar
pip install gunicorn
gunicorn main:app

# Or use Railway: railway up
```

### Frontend (Netlify - same as before)
```bash
git push origin main
# Netlify auto-deploys
```

---

## 12. Why Python + LLM Agents?

| Approach | Traditional Scraping | LLM Agents |
|----------|-------------------|-----------|
| **Brittleness** | Breaks on HTML changes | Robust to changes |
| **Maintenance** | High (constant fixes) | Low (LLM adapts) |
| **Speed** | Fast (parsing) | Slower (LLM call) |
| **Accuracy** | 90-95% | 95-99% |
| **Learning** | Lots of edge cases | Just prompt engineering |

**For hackathon:** LLM agents win on reliability and speed of development.

---

## 13. Success Metrics

✅ **Minimum:**
- Backend runs locally
- Frontend connects to backend
- Search returns prices for 3+ retailers
- Deployed (Netlify + Python server)

✅ **Competitive:**
- All 6 retailers working
- Review analysis displaying
- Fast searches (< 10 sec)
- Clean UI

---

## 14. API Endpoints

**Base URL:** `http://localhost:8000/api`

### POST /search
```json
Request: {"product_name": "Woodland sneaker"}
Response: {
  "product_name": "Woodland sneaker",
  "prices": [
    {"retailer": "FLIPKART", "price": 2499, ...},
    {"retailer": "AMAZON", "price": 2599, ...}
  ],
  "reviews": {
    "sentiment": {"positive": 78, "negative": 15, "neutral": 7},
    "pros": ["..."],
    "cons": [...]
  },
  "status": "success"
}
```

### GET /health
```json
Response: {"status": "healthy"}
```

---

**Timeline: 24-48 hours. Build the backend agents, connect frontend, deploy. 🚀**
