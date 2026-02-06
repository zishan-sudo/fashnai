# FashnAI Architecture Documentation

**Version:** 1.1
**Last Updated:** February 2026
**Project:** AI-Powered Fashion Product Comparison Platform

---

## Overview

FashnAI is a full-stack application that uses AI agents to compare fashion products across multiple e-commerce websites, analyze customer reviews, extract detailed product specifications, and provide AI-powered virtual try-on with personalized fit analysis and styling recommendations.

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERFACE                          │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  Next.js 14 Frontend (TypeScript)                   │  │
│  │  Port: 3000                                         │  │
│  │                                                      │  │
│  │  Components:                                        │  │
│  │  ├─ Home Page (Search Interface)                   │  │
│  │  ├─ Product Details Page (Tabbed Results)          │  │
│  │  │   ├─ Price Comparison Tab                       │  │
│  │  │   ├─ Review Analysis Tab                        │  │
│  │  │   └─ Product Specifications Tab                 │  │
│  │  └─ Virtual Try-On Page                            │  │
│  │      ├─ User Characteristics Input                 │  │
│  │      ├─ Photo Upload                               │  │
│  │      └─ AI-Generated Try-On Image                  │  │
│  └─────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ REST API (JSON)
                       │ - POST /api/search
                       │ - POST /api/prices
                       │ - POST /api/reviews
                       │ - POST /api/specs
                       │ - POST /api/virtual-tryon
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                   API GATEWAY                               │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  FastAPI Backend (Python)                           │  │
│  │  Port: 8000                                         │  │
│  │                                                      │  │
│  │  Features:                                          │  │
│  │  ├─ CORS Middleware (Frontend access)              │  │
│  │  ├─ Async Request Handling                         │  │
│  │  ├─ Parallel Agent Execution                       │  │
│  │  ├─ Error Handling & Retry Logic                   │  │
│  │  └─ Auto-generated API Docs (/docs)                │  │
│  └─────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ Agent Invocation
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                   AI AGENT LAYER                            │
│                   (Agno Framework)                          │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  ┌──────────┐ │
│  │ PriceAgent   │  │ Review       │  │ Specs    │  │ Virtual  │ │
│  │              │  │ Analyzer     │  │ Agent    │  │ TryOn    │ │
│  │ Finds product│  │ Analyzes     │  │ Extracts │  │ Provides │ │
│  │ across       │  │ reviews for  │  │ materials│  │ fit      │ │
│  │ fashion      │  │ sentiment,   │  │ sizes,   │  │ analysis │ │
│  │ retailers &  │  │ pros, cons,  │  │ features │  │ & styling│ │
│  │ prices       │  │ themes       │  │          │  │ advice   │ │
│  └──────┬───────┘  └──────┬───────┘  └────┬─────┘  └────┬─────┘ │
│         │                 │                │             │       │
│         └─────────────────┴────────────────┴─────────────┘       │
│                                 │                                │
│           Gemini 2.5 Flash API + Gemini 2.5 Flash Image         │
│                          (Google AI)                             │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ Tool Invocation
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                   TOOL LAYER                                │
│                                                             │
│  ┌──────────────────────┐    ┌──────────────────────┐     │
│  │  SerperTools         │    │  Crawl4aiTools       │     │
│  │  (Web Search)        │    │  (Web Scraping)      │     │
│  │                      │    │                      │     │
│  │  - Google Search API │    │  - Playwright        │     │
│  │  - Real-time results │    │  - Chromium browser  │     │
│  │  - Fashion retailers │    │  - JS rendering      │     │
│  └──────────┬───────────┘    └──────────┬───────────┘     │
│             │                           │                  │
└─────────────┴───────────────────────────┴──────────────────┘
              │                           │
              │                           │
┌─────────────▼───────────────────────────▼──────────────────┐
│              EXTERNAL DATA SOURCES                          │
│                                                             │
│  Fashion E-commerce Websites:                              │
│  ├─ Zalando, ASOS, Zara, H&M                              │
│  ├─ Nordstrom, Macy's, Bloomingdale's                     │
│  ├─ Farfetch, Net-a-Porter, Ssense                        │
│  ├─ Zappos, Foot Locker, StockX                           │
│  └─ Other fashion retailers                                │
│                                                             │
│  Product Information Extracted:                            │
│  ├─ Prices & Availability                                  │
│  ├─ Customer Reviews & Ratings                             │
│  ├─ Product Specifications                                 │
│  └─ Images & Descriptions                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. Frontend (TypeScript)

**Technology:** Next.js 14 with TypeScript, React 18, Tailwind CSS

**Structure:**
```
frontend/
├── app/
│   ├── page.tsx                    # Home/Search page
│   ├── product/[url]/page.tsx      # Product details page
│   ├── layout.tsx                  # Root layout
│   └── globals.css                 # Global styles
├── package.json                    # Dependencies
├── tsconfig.json                   # TypeScript config
└── tailwind.config.ts              # Tailwind config
```

**Key Features:**
- **Type Safety:** Full TypeScript coverage with strict mode
- **Responsive Design:** Mobile-first approach with Tailwind
- **State Management:** React hooks (useState, useEffect)
- **API Integration:** Axios for HTTP requests
- **Loading States:** Skeleton screens and spinners
- **Error Handling:** User-friendly error messages

**Pages:**

1. **Home Page (`/`)**
   - Search bar for product URL input
   - Feature showcase
   - "How It Works" section
   - Flash.co-inspired gradient design

2. **Product Details Page (`/product/[url]`)**
   - Tabbed interface (Prices, Reviews, Specs)
   - Price comparison with "Best Price" highlighting
   - Sentiment analysis visualization
   - Comprehensive specifications display

---

### 2. Backend (Python)

**Technology:** FastAPI, Python 3.13

**Structure:**
```
backend/
├── api.py                          # FastAPI server
├── PriceAgent.py                   # Price comparison agent
├── ReviewAnalyzerAgent.py          # Review analysis agent
├── ProductSpecsAgent.py            # Specifications agent
├── VirtualTryOnAgent.py            # Virtual try-on AI agent
├── api_key_manager.py              # API key rotation manager
└── playground.py                   # AgentOS playground
```

**API Endpoints:**

| Endpoint | Method | Description | Response Time |
|----------|--------|-------------|---------------|
| `/` | GET | API information | <100ms |
| `/health` | GET | Health check | <100ms |
| `/api/search` | POST | Complete analysis (all 3 agents) | 30-60s |
| `/api/prices` | POST | Price comparison only | 10-20s |
| `/api/reviews` | POST | Review analysis only | 10-20s |
| `/api/specs` | POST | Product specifications only | 10-20s |
| `/api/virtual-tryon` | POST | Virtual try-on with fit analysis | 15-30s |

**Key Features:**
- **Async Processing:** Parallel agent execution
- **CORS Support:** Frontend access from any origin
- **Error Handling:** Comprehensive exception handling
- **Retry Logic:** Up to 3 retries per agent
- **Logging:** Structured logging for debugging

---

### 3. AI Agents (Agno Framework)

#### 3.1 PriceAgent

**Purpose:** Find and compare prices across fashion retailers

**Process:**
1. Extract product details from input URL
2. Search for same product on other retailers
3. Verify exact product match
4. Extract prices and availability
5. Return sorted results (cheapest first)

**Output Schema:**
```typescript
{
  original_product_name: string;
  original_product_url: string;
  product_listings: Array<{
    website_name: string;
    product_url: string;
    price: string;
    availability: string;
    seller_info: string;
  }>;
  search_summary: string;
  sources_checked: string[];
}
```

#### 3.2 ReviewAnalyzerAgent

**Purpose:** Analyze customer reviews for sentiment and insights

**Process:**
1. Find product reviews from multiple sources
2. Analyze sentiment (positive/negative/neutral)
3. Extract common pros and cons
4. Identify recurring themes
5. Generate summary

**Output Schema:**
```typescript
{
  overall_rating: number;
  total_reviews: number;
  sentiment: {
    positive: number;
    negative: number;
    neutral: number;
  };
  pros: string[];
  cons: string[];
  common_themes: string[];
  summary: string;
  verified_purchase_percentage: number;
  sources_analyzed: string[];
}
```

#### 3.3 ProductSpecsAgent

**Purpose:** Extract comprehensive product specifications

**Process:**
1. Crawl product page for specifications
2. Extract material, sizes, care instructions
3. Identify key features
4. Search for additional information if needed
5. Return structured specifications

**Output Schema:**
```typescript
{
  product_name: string;
  brand: string;
  category: string;
  color: string;
  material: string;
  sizes_available: string[];
  care_instructions: string | null;
  features: string[];
  fit_type: string | null;
  style_number: string | null;
  country_of_origin: string | null;
  sustainability: string | null;
  sources: string[];
}
```

#### 3.4 VirtualTryOnAgent

**Purpose:** Provide AI-powered virtual try-on with personalized fit analysis and styling recommendations

**Process:**
1. Analyze product details (with optional pre-fetched specs to avoid re-crawling)
2. Process user characteristics (size, height, body type)
3. Analyze user photo if provided (using Gemini Vision)
4. Generate realistic try-on image using Gemini 2.5 Flash Image
5. Provide fit analysis based on body type and garment specifications
6. Recommend optimal size
7. Generate 3-5 personalized styling suggestions
8. Assign confidence score (0.0-1.0)

**Output Schema:**
```typescript
{
  generated_image_description: string;        // Detailed description of how garment looks on user
  fit_analysis: string;                       // Analysis of garment fit on user's body type
  style_recommendations: string[];            // 3-5 styling suggestions
  confidence_score: number;                   // 0.0-1.0 reliability score
  size_recommendation: string;                // Recommended size based on specs & measurements
  product_name: string;                       // Name of product being tried on
  warnings: string[];                         // Warnings about fit, style, compatibility
  generated_image_base64: string | null;      // Base64 encoded generated try-on image
}
```

**Key Features:**
- **Image Generation:** Uses Gemini 2.5 Flash Image to create realistic try-on photos
- **Cached Product Specs:** Accepts pre-fetched product data to avoid redundant crawling
- **User Photo Analysis:** Processes user photos to determine body shape and proportions
- **Personalized Recommendations:** Tailored advice based on user characteristics
- **Confidence Scoring:** Transparent reliability assessment

---

### 4. Tools & Services

#### 4.1 SerperTools (Web Search)

- **Provider:** Serper.dev
- **Purpose:** Real-time Google search results
- **Usage:** Finding product listings across retailers
- **Rate Limit:** Based on API plan
- **Cost:** Pay-per-search

#### 4.2 Crawl4aiTools (Web Scraping)

- **Technology:** Playwright + Chromium
- **Purpose:** Extract content from web pages
- **Features:**
  - JavaScript rendering
  - Dynamic content loading
  - Anti-bot detection handling
- **Max Content:** 12,000-15,000 characters per page

#### 4.3 Google Gemini API

- **Models:**
  - Gemini 2.5 Flash (text analysis & extraction)
  - Gemini 2.5 Flash Image (virtual try-on image generation)
- **Purpose:** Intelligent data extraction, analysis, and image generation
- **Features:**
  - Fast response times
  - Structured output (JSON mode)
  - Multi-turn conversations
  - Tool calling support
  - Vision capabilities (image analysis)
  - Image generation (try-on photos)
- **Authentication:** API key (GOOGLE_API_KEY_1, _2, _3)

---

## Data Flow

### Complete Search Flow

```
1. User enters product URL
   ↓
2. Frontend sends POST /api/search
   ↓
3. Backend creates 3 async tasks:
   ├─ PriceAgent.compare_prices()
   ├─ ReviewAnalyzerAgent.analyze_reviews()
   └─ ProductSpecsAgent.extract_specifications()
   ↓
4. Each agent:
   ├─ Crawls product URL
   ├─ Searches for additional sources
   ├─ Calls Gemini API for analysis
   └─ Returns structured data
   ↓
5. Backend aggregates results
   ↓
6. Frontend receives complete analysis
   ↓
7. User views results in tabbed interface
```

**Timing:**
- Frontend → Backend: ~50ms
- Agent execution (parallel): 30-60s
- Backend → Frontend: ~50ms
- **Total:** ~30-60 seconds

### Virtual Try-On Flow

```
1. User navigates to Virtual Try-On page
   ↓
2. User inputs characteristics (size, height, body type)
3. User optionally uploads photo
   ↓
4. Frontend sends POST /api/virtual-tryon
   ├─ product_url
   ├─ user_size, user_height, user_body_type
   ├─ user_image_base64 (optional)
   └─ product_specs (cached from previous analysis)
   ↓
5. VirtualTryOnAgent:
   ├─ Analyzes product details (or uses cached specs)
   ├─ Processes user photo with Gemini Vision (if provided)
   ├─ Generates try-on image with Gemini 2.5 Flash Image
   ├─ Analyzes fit based on body type & garment specs
   ├─ Recommends size
   ├─ Generates styling suggestions
   └─ Returns VirtualTryOnResult
   ↓
6. Frontend displays:
   ├─ Generated try-on image
   ├─ Fit analysis
   ├─ Size recommendation
   ├─ Styling suggestions
   └─ Confidence score & warnings
```

**Timing:**
- Frontend → Backend: ~50ms
- Product analysis (or cached): 0-10s
- User photo processing: 2-5s
- Image generation: 5-10s
- Fit analysis & recommendations: 3-5s
- Backend → Frontend: ~50ms
- **Total:** ~15-30 seconds (varies with image generation)

---

## Database Schema

**Technology:** SQLite (via Agno)

**Tables:**
- `price_comparison_agent` - Price agent sessions
- `review_analyzer_agent` - Review agent sessions
- `product_specs_agent` - Specs agent sessions
- `virtual_tryon_agent` - Virtual try-on agent sessions

**Purpose:** Store agent conversation history and state

---

## Security

### API Keys
- Stored in `.env` file (not in version control)
- Loaded via `python-dotenv`
- Required keys:
  - `GOOGLE_API_KEY_1` - Gemini API (PriceAgent & VirtualTryOnAgent)
  - `GOOGLE_API_KEY_2` - Gemini API (ReviewAnalyzerAgent)
  - `GOOGLE_API_KEY_3` - Gemini API (ProductSpecsAgent)
  - `SERPER_API_KEY` - Serper search API

### CORS
- Configured to allow frontend origins
- Supports credentials
- All methods and headers allowed

### Input Validation
- Pydantic models for request validation
- URL format validation
- Error handling for malformed requests

---

## Performance Optimization

### Backend
- **Parallel Execution:** All 3 agents run simultaneously
- **Async I/O:** Non-blocking HTTP requests
- **Connection Pooling:** Reuse HTTP connections
- **Retry Logic:** Exponential backoff for failures

### Frontend
- **Code Splitting:** Next.js automatic code splitting
- **Image Optimization:** Next.js image component
- **Lazy Loading:** Components loaded on demand
- **Caching:** Browser caching for static assets

---

## Deployment

### Backend Deployment Options

1. **Local Development**
   ```bash
   cd backend
   python api.py
   ```

2. **Production (Railway/Render)**
   - Automatic deployment from Git
   - Environment variables configured
   - Health check endpoint: `/health`

### Frontend Deployment Options

1. **Local Development**
   ```bash
   cd frontend
   npm run dev
   ```

2. **Production (Vercel/Netlify)**
   - Automatic deployment from Git
   - Environment variable: `NEXT_PUBLIC_API_URL`
   - Edge network distribution

---

## Monitoring & Logging

### Backend Logging
- Structured logging with Python `logging` module
- Log levels: INFO, WARNING, ERROR
- Logged events:
  - API requests
  - Agent execution start/end
  - Errors and exceptions
  - Performance metrics

### Error Tracking
- HTTP status codes
- Exception messages
- Stack traces in logs

---

## Future Enhancements

### Planned Features
1. **Caching Layer:** Redis for repeated searches
2. **Price History:** Track price changes over time
3. **Price Alerts:** Notify users of price drops
4. **User Accounts:** Save favorite products and try-on results
5. **Affiliate Links:** Monetization through affiliate programs
6. **More Retailers:** Expand to 20+ fashion websites
7. **Image Search:** Find products by image
8. ~~**Size Recommendations:** AI-powered fit suggestions~~ ✅ **COMPLETED** (Virtual Try-On feature)
9. **Enhanced Virtual Try-On:**
   - Full-body visualization
   - Multiple outfit combinations
   - AR try-on using device camera
10. **Body Measurement Tools:** Guide users to measure themselves accurately
11. **Style Profile:** Learn user preferences over time for better recommendations

### Technical Improvements
1. **Rate Limiting:** Prevent API abuse
2. **Database:** PostgreSQL for production
3. **Queue System:** Celery for background tasks
4. **Monitoring:** Prometheus + Grafana
5. **Testing:** Comprehensive test suite
6. **CI/CD:** Automated testing and deployment

---

## Development Workflow

### Setup
1. Clone repository
2. Install backend dependencies: `uv sync`
3. Install frontend dependencies: `npm install`
4. Configure `.env` files
5. Install Playwright: `playwright install chromium`

### Running Locally
1. Start backend: `python backend/api.py`
2. Start frontend: `npm run dev` (in frontend/)
3. Access at `http://localhost:3000`

### Testing
1. Test individual agents:
   - `python backend/PriceAgent.py`
   - `python backend/ReviewAnalyzerAgent.py`
   - `python backend/ProductSpecsAgent.py`
   - `python backend/VirtualTryOnAgent.py`
2. Test API: `curl http://localhost:8000/health`
3. Test frontend: Open browser to `localhost:3000`

---

**Document Version:** 1.1
**Last Updated:** February 6, 2026
**Maintained By:** FashnAI Development Team

**Changelog:**
- **v1.1 (Feb 2026):** Added Virtual Try-On agent with AI image generation
- **v1.0 (Jan 2026):** Initial architecture with 3 agents (Price, Review, Specs)
