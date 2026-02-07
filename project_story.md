# FashionAI - AI-Powered Fashion Shopping Assistant

## Introduction

You find a jacket you love online — but is it cheaper somewhere else? Will it actually fit? Today you'd open a dozen tabs, compare prices manually, scroll through conflicting reviews, and still have no idea how it looks on you. FashionAI fixes this. Paste a single product URL and our AI agents instantly scan the web in parallel: one hunts down the same item across competing retailers and surfaces the best price, while others extract detailed specs and summarize customer reviews. But the real game-changer is our virtual try-on — upload a photo of yourself and FashionAI generates a realistic image of you wearing the garment, powered by Google Gemini's multimodal image generation. No more guessing if that dress flatters your body type or if you should size up. FashionAI solves this: a 30-second end-to-end analysis that replaces an hour of tab-hopping — and could cut fashion e-commerce return rates, which currently run as high as 40%, by helping shoppers make confident purchase decisions before clicking "Buy."

## What It Does

FashionAI is a multi-agent AI system that takes a product URL and runs **four specialized agents** to deliver a comprehensive shopping analysis:

| Agent | Purpose |
|---|---|
| **PriceAgent** | Crawls the product page, searches for the same item across competing retailers, and returns a structured price comparison with direct links |
| **ReviewAnalyzerAgent** | Aggregates customer reviews from multiple sources and extracts sentiment scores, pros/cons, recurring themes, and a concise summary |
| **ProductSpecsAgent** | Extracts detailed product specifications — material, sizing, care instructions, fit type, sustainability info — even when spread across multiple page sections |
| **VirtualTryOnAgent** | Accepts an optional user photo and body measurements, then generates a realistic AI image of the user wearing the product along with fit analysis and size recommendations |

The first three agents execute **in parallel** on the backend, reducing total analysis time from ~90 seconds (sequential) to ~30–40 seconds. The virtual try-on runs as a separate step, optionally reusing cached product specs to avoid redundant crawling.

## How We Built It

### Architecture

```
┌──────────────┐       ┌──────────────────────────────────────────┐
│  Next.js 14  │       │            FastAPI Backend               │
│  (Frontend)  │──────▶│                                          │
│  Tailwind    │  REST │  asyncio.gather(                         │
│  TypeScript  │◀──────│    PriceAgent,                           │
└──────────────┘       │    ReviewAnalyzerAgent,    ← parallel    │
                       │    ProductSpecsAgent                     │
                       │  )                                       │
                       │                                          │
                       │  VirtualTryOnAgent  ← separate endpoint  │
                       │    └─ Gemini Image Generation            │
                       └──────────────────────────────────────────┘
```

### Tech Stack

- **Backend:** Python 3.13, FastAPI, Uvicorn, Pydantic for structured output schemas
- **Agent Framework:** [Agno](https://github.com/agno-agi/agno) — each agent is an `Agent` instance with its own tools, instructions, and Pydantic output model
- **LLM:** Google Gemini (text reasoning) + Gemini Image (virtual try-on generation)
- **Web Search:** Serper API (Google Search) via `SerperTools`
- **Web Scraping:** Crawl4ai — async web crawler that extracts clean text from dynamic fashion sites
- **Image Processing:** Pillow (PIL) for decoding user photos; Gemini multimodal API for generating try-on images
- **Frontend:** Next.js 14 (App Router), React 18, Tailwind CSS, Axios
- **Data:** SQLite (via Agno's `SqliteDb`) for agent session persistence; `sessionStorage` for client-side spec caching

### Parallel Agent Execution

The core insight was that price comparison, review analysis, and spec extraction are **independent tasks** on the same product URL. We run them concurrently:

```python
price_task = asyncio.create_task(asyncio.to_thread(compare_prices, product_url))
review_task = asyncio.create_task(asyncio.to_thread(analyze_reviews, product_url))
specs_task = asyncio.create_task(asyncio.to_thread(extract_specifications, product_url))

results = await asyncio.gather(price_task, review_task, specs_task, return_exceptions=True)
```

Each agent runs in its own thread (Agno agents are synchronous), while the FastAPI event loop coordinates them asynchronously.

### Virtual Try-On Pipeline

1. User uploads a photo and enters size/height/body type
2. Frontend converts the photo to base64 and sends it alongside cached product specs
3. The `VirtualTryOnAgent` performs fit analysis using Gemini
4. A separate `generate_tryon_image()` function calls Gemini Image with the user photo + product description
5. The generated image is base64-encoded and returned to the frontend for display

## Challenges

**Rate limiting on Gemini's free tier.** Running three agents in parallel — each making multiple tool calls (search + crawl) — quickly hit rate limits. We mitigated this with an `APIKeyManager` that rotates across multiple API keys, and the frontend falls back to sequential calls with 20-second delays between agents when needed.

**Coordinating parallel agents with graceful failure.** If one agent fails (e.g., a site blocks the crawler), the other two should still return results. We use `return_exceptions=True` in `asyncio.gather` and substitute default Pydantic models with error messages for any failed agent.

**Web scraping dynamic fashion sites.** Product pages on Zalando, ASOS, and similar sites rely heavily on JavaScript rendering, lazy-loaded content, and anti-bot measures. Crawl4ai's async browser-based crawling handles most of this, but we still had to tune `max_length` parameters per agent to balance completeness against token limits.

**Generating realistic try-on images.** Getting Gemini's image generation to produce natural-looking results — preserving the user's face, body proportions, and background while fitting a new garment — required careful prompt engineering. The prompt explicitly instructs the model to maintain the person's identity and only modify the clothing.

## What We Learned

**Multi-agent orchestration is about boundaries.** The key design decision was giving each agent a narrow, well-defined task with a strict Pydantic output schema. This made agents composable and independently testable. The Agno framework's `output_schema` + `use_json_mode=True` pattern was critical for getting structured, parseable results.

**Prompt engineering for structured extraction.** Getting an LLM to reliably extract product specs from messy HTML required very specific instructions — listing every field to extract, providing examples, and using `tool_call_limit` to prevent agents from endlessly searching.

**Letting the LLM handle scoring.** Rather than hand-coding sentiment formulas, we delegate scoring entirely to Gemini via structured output schemas. The `ReviewAnalyzerAgent` returns a `SentimentScore` with positive/negative/neutral percentages, and the `VirtualTryOnAgent` returns a `confidence_score` float (0.0–1.0) — both determined by the LLM's reasoning over the scraped data. The agent instructions guide what factors to weigh (verified-purchase status, review substantiveness, completeness of user-provided characteristics), but the model applies its own judgement. This turned out to be more robust than a rigid formula, since the LLM can account for context a static equation can't — like a product with only 3 reviews versus 300, or a user who provided a photo but no size.

**Real-world web scraping is messy.** Sites change layouts, block bots, serve different content to different user agents, and paginate reviews differently. Building resilience into each agent — retry logic (up to 3 attempts), fallback search queries, and graceful degradation — was essential.

## What's Next

- **Size chart normalization** — Build a universal sizing database so "Medium" on Zalando, "M" on ASOS, and "Size 10" on a UK site all map to the same measurements
- **Price history tracking** — Store historical prices and alert users when items drop below a target price
- **Outfit coordination** — Recommend complementary pieces (shoes, accessories) based on the analyzed product's style and color
- **Multi-garment try-on** — Generate try-on images with complete outfits rather than single items
- **Browser extension** — Surface FashionAI analysis directly on product pages without leaving the retailer's site
- **User preference learning** — Track which styles, brands, and fits a user prefers and personalize recommendations over time

