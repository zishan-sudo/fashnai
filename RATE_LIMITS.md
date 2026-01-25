# Gemini API Rate Limits & Solutions

## Current Issue

The Gemini API free tier has strict rate limits:
- **5 requests per minute** for `gemini-2.5-flash` model
- When exceeded, you get a `RESOURCE_EXHAUSTED` error with a retry delay (typically 50-60 seconds)

## How It Affects FashnAI

FashnAI uses 3 AI agents that each make multiple Gemini API calls:
1. **PriceAgent** - 2-3 API calls
2. **ReviewAnalyzerAgent** - 2-3 API calls  
3. **ProductSpecsAgent** - 2-3 API calls

**Total**: 6-9 API calls per product search, which exceeds the 5/minute limit.

## Current Solution (Implemented)

### Sequential Execution with Delays
The backend now runs agents **sequentially** with 15-second delays between them:

```python
# Price agent (takes ~20s)
price_result = await asyncio.to_thread(compare_prices, url)
await asyncio.sleep(15)  # Wait 15s

# Review agent (takes ~20s)
review_result = await asyncio.to_thread(analyze_reviews, url)
await asyncio.sleep(15)  # Wait 15s

# Specs agent (takes ~20s)
specs_result = await asyncio.to_thread(extract_specifications, url)
```

**Total time**: ~70 seconds per complete search

### Graceful Error Handling
If any agent hits the rate limit, it returns a default/empty response instead of crashing:

```json
{
  "summary": "Review analysis unavailable due to API rate limit. Please try again in a few minutes.",
  "overall_rating": 0.0,
  "total_reviews": 0,
  ...
}
```

## Better Solutions

### Option 1: Upgrade to Paid Tier (Recommended)
**Cost**: Pay-as-you-go pricing
- **Rate Limit**: 1000 requests/minute
- **Cost**: ~$0.00001875 per request (very cheap)
- **Benefits**: No delays needed, parallel execution, faster responses

**Setup**:
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Enable billing
3. Use the same API key (automatically upgraded)

### Option 2: Use Multiple API Keys (Free)
Rotate between multiple free-tier API keys:

```python
API_KEYS = [
    os.getenv("GOOGLE_API_KEY_1"),
    os.getenv("GOOGLE_API_KEY_2"),
    os.getenv("GOOGLE_API_KEY_3"),
]

# Rotate keys for each agent
price_agent = Agent(api_key=API_KEYS[0])
review_agent = Agent(api_key=API_KEYS[1])
specs_agent = Agent(api_key=API_KEYS[2])
```

**Benefits**: 15 requests/minute total (5 per key × 3 keys)
**Drawbacks**: Need to manage multiple accounts

### Option 3: Implement Caching (Partial Solution)
Cache results for frequently searched products:

```python
# Redis cache
cache_key = f"product:{hash(product_url)}"
cached_result = redis.get(cache_key)
if cached_result:
    return cached_result

# Run agents...
redis.setex(cache_key, 3600, result)  # Cache for 1 hour
```

**Benefits**: Instant results for cached products
**Drawbacks**: Only helps with repeated searches

### Option 4: Queue System (Advanced)
Implement a job queue for background processing:

```python
# User submits search
job_id = queue.enqueue(analyze_product, product_url)
return {"job_id": job_id, "status": "processing"}

# User polls for results
GET /api/jobs/{job_id}
```

**Benefits**: Better user experience, no timeouts
**Drawbacks**: More complex architecture

## Testing with Rate Limits

### Test Individual Agents
Test one agent at a time to avoid hitting limits:

```bash
# Test price agent only
curl -X POST http://localhost:8000/api/prices \
  -H "Content-Type: application/json" \
  -d '{"product_url": "https://en.zalando.de/..."}'

# Wait 60 seconds before next test

# Test review agent
curl -X POST http://localhost:8000/api/reviews \
  -H "Content-Type: application/json" \
  -d '{"product_url": "https://en.zalando.de/..."}'
```

### Test Complete Search
Allow 70+ seconds for complete search:

```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"product_url": "https://en.zalando.de/..."}'

# Takes ~70 seconds to complete
```

### Monitor Rate Limit Status
Check Gemini API usage:
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Click on "API Keys"
3. View usage metrics

## Production Recommendations

For production deployment:

1. **Upgrade to Paid Tier** ($5-10/month for moderate usage)
2. **Implement Redis Caching** (reduce API calls by 60-80%)
3. **Add Rate Limit Monitoring** (track usage, alert on limits)
4. **Use Job Queue** (better UX for slow operations)
5. **Consider Alternative Models** (Claude, GPT-4 have different limits)

## Current Status

✅ **Error handling implemented** - Graceful fallbacks when rate limited
✅ **Sequential execution** - Avoids parallel rate limit issues  
✅ **Delays added** - 15s between agents to spread requests
⚠️ **Slow response time** - 70 seconds per complete search
⚠️ **Still hits limits** - Each agent makes multiple calls

**Recommendation**: Upgrade to paid tier for production use.

---

**Document Version:** 1.0  
**Last Updated:** January 25, 2026  
**Maintained By:** FashnAI Development Team
