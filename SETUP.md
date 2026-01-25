# FashnAI - Setup and Testing Guide

## Overview
FashnAI is an AI-powered fashion product comparison platform with:
- **Backend**: Python FastAPI with 3 AI agents (Price Comparison, Review Analysis, Product Specs)
- **Frontend**: Next.js with Flash.co-inspired design
- **AI**: Gemini 2.5 Flash for intelligent web scraping and analysis

---

## Backend Setup

### 1. Install Dependencies
```bash
cd /home/zishan/PycharmProjects/fashnai
source .venv/bin/activate
uv sync
```

### 2. Install Playwright Browsers
```bash
source .venv/bin/activate
python -m playwright install chromium
```

### 3. Configure Environment Variables
Ensure `.env` file has:
```
SERPER_API_KEY=your-serper-api-key
GOOGLE_API_KEY_1=your-first-gemini-api-key
GOOGLE_API_KEY_2=your-second-gemini-api-key
GOOGLE_API_KEY_3=your-third-gemini-api-key
```

### 4. Test Individual Agents

#### Test Price Agent
```bash
cd backend
python PriceAgent.py
```

#### Test Review Analyzer
```bash
cd backend
python ReviewAnalyzerAgent.py
```

#### Test Product Specs Agent
```bash
cd backend
python ProductSpecsAgent.py
```

### 5. Start FastAPI Server
```bash
cd backend
python api.py
```

Server will run on: `http://localhost:8000`

API Endpoints:
- `GET /` - API info
- `GET /health` - Health check
- `POST /api/search` - Complete analysis (prices + reviews + specs)
- `POST /api/prices` - Price comparison only
- `POST /api/reviews` - Review analysis only
- `POST /api/specs` - Product specifications only

### 6. Test API with curl
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test complete search (this will take 30-60 seconds)
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"product_url": "https://en.zalando.de/bershka-baby-gifts-black-bej22s0jx-q11.html"}'

# Test price comparison only
curl -X POST http://localhost:8000/api/prices \
  -H "Content-Type: application/json" \
  -d '{"product_url": "https://en.zalando.de/bershka-baby-gifts-black-bej22s0jx-q11.html"}'
```

---

## Frontend Setup

### 1. Install Node.js and npm
```bash
# Check if Node.js is installed
node --version
npm --version

# If not installed:
sudo apt update
sudo apt install nodejs npm
```

### 2. Install Frontend Dependencies
```bash
cd /home/zishan/PycharmProjects/fashnai/frontend
npm install
```

### 3. Start Development Server
```bash
npm run dev
```

Frontend will run on: `http://localhost:3000`

---

## Testing the Complete System

### 1. Start Backend (Terminal 1)
```bash
cd /home/zishan/PycharmProjects/fashnai/backend
source ../.venv/bin/activate
python api.py
```

### 2. Start Frontend (Terminal 2)
```bash
cd /home/zishan/PycharmProjects/fashnai/frontend
npm run dev
```

### 3. Test in Browser
1. Open `http://localhost:3000`
2. Paste a product URL (e.g., `https://en.zalando.de/bershka-baby-gifts-black-bej22s0jx-q11.html`)
3. Click "Compare"
4. **Wait 60-90 seconds** for AI analysis (slow due to rate limits)
5. View results in three tabs:
   - **Price Comparison**: Prices across multiple retailers
   - **Reviews**: Sentiment analysis, pros/cons, summary
   - **Specifications**: Product details, materials, sizes

### ⚠️ Important: Gemini API Rate Limits

The **free tier** of Gemini API has strict limits:
- **5 requests per minute**
- Each product search uses 6-9 API calls (3 agents × 2-3 calls each)

**Current Behavior**:
- Agents run **sequentially** with 15-second delays to avoid rate limits
- Total time: **60-90 seconds** per search
- If rate limit is hit, you'll see placeholder data with a message

**Solutions**:
1. **Upgrade to paid tier** (recommended for production) - 1000 req/min, ~$0.02 per search
2. **Use multiple API keys** - Rotate between 3 keys for 15 req/min total
3. **Wait between searches** - Allow 60+ seconds between tests

See `RATE_LIMITS.md` for detailed solutions.

---

## Test URLs

Try these fashion product URLs:

1. **Zalando**:
   - `https://en.zalando.de/bershka-baby-gifts-black-bej22s0jx-q11.html`

2. **ASOS**:
   - `https://www.asos.com/nike/nike-air-force-1-07-trainers-in-white/prd/...`

3. **H&M**:
   - `https://www2.hm.com/en_us/productpage...`

4. **Zara**:
   - `https://www.zara.com/us/en/...`

---

## Project Structure

```
styleiq/
├── backend/
│   ├── PriceAgent.py              # Price comparison agent
│   ├── ReviewAnalyzerAgent.py     # Review analysis agent
│   ├── ProductSpecsAgent.py       # Product specs agent
│   ├── api.py                     # FastAPI server
│   └── playground.py              # AgentOS playground (optional)
├── frontend/
│   ├── app/
│   │   ├── page.tsx               # Home/search page
│   │   ├── product/[url]/page.tsx # Product details page
│   │   ├── layout.tsx             # Root layout
│   │   └── globals.css            # Global styles
│   ├── package.json               # Dependencies
│   └── .env.local                 # API URL config
├── .env                           # Backend API keys
└── README.md                      # Project documentation
```

---

## Features

### 1. Price Comparison Agent
- Searches for product across multiple fashion retailers
- Extracts prices, availability, and seller info
- Identifies best deals
- **Test**: `python backend/PriceAgent.py`

### 2. Review Analyzer Agent
- Analyzes customer reviews from multiple sources
- Sentiment analysis (positive/negative/neutral)
- Extracts pros and cons
- Identifies common themes
- **Test**: `python backend/ReviewAnalyzerAgent.py`

### 3. Product Specs Agent
- Extracts comprehensive product specifications
- Material composition, care instructions
- Available sizes, fit type
- Key features and sustainability info
- **Test**: `python backend/ProductSpecsAgent.py`

### 4. Flash.co-Inspired Frontend
- Modern, clean UI with gradient backgrounds
- Responsive design (mobile-friendly)
- Real-time loading states
- Tabbed interface for prices/reviews/specs
- Direct links to retailer websites

---

## Troubleshooting

### Backend Issues

**Issue**: `ModuleNotFoundError: No module named 'agno'`
```bash
source .venv/bin/activate
uv sync
```

**Issue**: `Playwright browser not found`
```bash
source .venv/bin/activate
python -m playwright install chromium
```

**Issue**: `Error from Gemini API: 404 NOT_FOUND`
- Check `GOOGLE_API_KEY` in `.env`
- Verify model ID is `gemini-2.5-flash` or `gemini-2.0-flash-exp`

**Issue**: `CORS error from frontend`
- Ensure FastAPI server is running on port 8000
- Check CORS middleware in `api.py`

### Frontend Issues

**Issue**: `Cannot find module 'next'`
```bash
cd frontend
npm install
```

**Issue**: `Connection refused to localhost:8000`
- Start backend server first: `python backend/api.py`

**Issue**: `Page stuck on loading`
- Check browser console for errors
- Verify backend is responding: `curl http://localhost:8000/health`
- AI analysis takes 30-60 seconds - be patient!

---

## Performance Notes

- **Analysis Time**: 30-60 seconds per product (3 agents running in parallel)
- **Rate Limits**: Gemini API has rate limits - add delays if needed
- **Caching**: Consider adding Redis for repeated searches
- **Optimization**: Agents run in parallel for faster results

---

## Next Steps

1. **Add More Retailers**: Extend search to more fashion websites
2. **Price History**: Track price changes over time
3. **Alerts**: Notify users when prices drop
4. **User Accounts**: Save favorite products
5. **Mobile App**: React Native version
6. **Affiliate Links**: Monetize with affiliate programs

---

## API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI)

---

## Support

For issues or questions:
1. Check logs in terminal
2. Verify API keys are valid
3. Test individual agents first
4. Check network connectivity

---

**Happy Testing! 🚀**
