# FashnAI

AI-powered fashion research and price comparison system using multi-agent architecture. Specialized in apparel and footwear analysis.

## Features

- **Fashion Price Comparison Agent**: Finds the same fashion product (clothing, shoes, accessories) across multiple fashion e-commerce websites and compares prices
- **Review Analysis Agent**: Analyzes customer reviews, sentiment, pros/cons, and provides comprehensive insights
- **Product Specifications Agent**: Extracts detailed product specifications including materials, sizes, care instructions, and features
- **Virtual Try-On AI**: AI-powered virtual try-on that provides personalized fit analysis, size recommendations, and styling suggestions based on user characteristics

## Prerequisites

- Python 3.13 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- Node.js 18+ and npm (for frontend)
- Gemini API key (for Google AI)
- Serper API key (for web search)

## Installation

### 1. Install uv

If you don't have `uv` installed, install it using:

```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Clone the Repository

```bash
git clone <repository-url>
cd fashnai
```

### 3. Set Up Environment

Create a `.env` file in the project root with the following variables:

```env
GOOGLE_API_KEY=your-google-api-key
SERPER_API_KEY=your-serper-api-key
```

**Note:** For production with multiple API keys to avoid rate limits, you can use:
```env
GOOGLE_API_KEY_1=your-first-google-api-key
GOOGLE_API_KEY_2=your-second-google-api-key
GOOGLE_API_KEY_3=your-third-google-api-key
SERPER_API_KEY=your-serper-api-key
```

**Required API Keys:**
- **Gemini API**: Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
- **Serper API**: Get your API key from [serper.dev](https://serper.dev)

### 4. Install Dependencies

**Backend Dependencies:**
Use `uv sync` to create a virtual environment and install all dependencies:

```bash
uv sync
```

This command will:
- Create a virtual environment in `.venv/`
- Install all dependencies specified in `pyproject.toml`
- Lock dependencies for reproducibility

**Frontend Dependencies:**
```bash
cd frontend
npm install
cd ..
```

### 5. Activate Virtual Environment

```bash
# On Linux/macOS
source .venv/bin/activate

# On Windows
.venv\Scripts\activate
```

### 6. Setup crawl4ai to install browser tools
```bash
source .venv/bin/activate
crawl4ai-setup
```

### 7. To Enable debugging
```bash
export AGNO_DEBUG=true
```

## Usage

### Quick Start - Run Everything

To start the full application (backend + frontend):

```bash
./start.sh
```

This will start:
- **Backend (Agents)**: http://localhost:8000
- **Frontend**: http://localhost:3000

To stop all services, press `Ctrl+C`.

View logs:
```bash
# Backend logs
tail -f backend_log.txt

# Frontend logs
tail -f frontend_log.txt
```

### Manual Start

**Start Backend API Server:**
```bash
uv run backend/api.py
```

**Start Frontend:**
```bash
cd frontend
npm run dev
```

**Alternative - AgentOS Playground (for testing agents directly):**
```bash
uv run backend/playground.py
```
Note: The playground is for agent testing with AgentOS UI, not for the web frontend.

### Using the Web Application

1. **Search for a Product**: Paste any fashion product URL on the home page
2. **View Analysis**: See price comparisons, reviews, and specifications
3. **Try Virtual Try-On**: Click the "Try Virtual Try-On" button on any product page
4. **Get Personalized Insights**: Enter your size, height, and body type for AI-powered fit analysis and styling recommendations

### Fashion Price Comparison Agent

Compare prices for fashion products (apparel, shoes, accessories) across multiple fashion e-commerce websites:

```python
from backend.PriceAgent import compare_prices

# Example with a fashion product URL
result = compare_prices("https://www.asos.com/product/example-dress")
print(result.content)
```

### Virtual Try-On Agent

Get AI-powered fit analysis and styling recommendations:

```python
from backend.VirtualTryOnAgent import virtual_tryon

# Example with user characteristics
result = virtual_tryon(
    product_url="https://en.zalando.de/bershka-baby-gifts-black-bej22s0jx-q11.html",
    user_size="M",
    user_height="5'9\"",
    user_body_type="athletic"
)
print(result.content)
```

### AgentOS Integration
- Rename .env-template to .env and set the API Keys
- Is necessary to create an account with agno to use the playground, even locally
- Connect to AgentOS UI for a readymade interface to interact with the agent as mentioned here https://docs.agno.com/introduction

## Project Structure

```
fashnai/
├── backend/
│   ├── PriceAgent.py            # Fashion price comparison agent
│   ├── ReviewAnalyzerAgent.py   # Review analysis agent
│   ├── ProductSpecsAgent.py     # Product specifications agent
│   ├── VirtualTryOnAgent.py     # Virtual try-on AI agent
│   ├── api.py                   # FastAPI server
│   ├── api_key_manager.py       # API key management
│   └── playground.py            # AgentOS playground
├── frontend/                    # Next.js frontend application
│   ├── app/
│   │   ├── page.tsx            # Home page
│   │   ├── product/[url]/      # Product details page
│   │   ├── try-on/             # Virtual try-on page
│   │   └── layout.tsx          # App layout
│   ├── package.json            # Frontend dependencies
│   └── ...
├── .env                        # Environment variables (not in git)
├── pyproject.toml              # Backend dependencies
├── start.sh                    # Startup script for full application
└── README.md                   # This file
```

## Dependencies

**Backend:**
- **agno**: Multi-agent framework
- **google-genai**: Google Gemini AI models (including Vision API for virtual try-on)
- **crawl4ai**: Web scraping and crawling
- **google-search-results**: Serper API integration
- **fastapi**: REST API framework
- **pillow**: Image processing
- **pydantic**: Data validation and schema definition

**Frontend:**
- **Next.js 14**: React framework
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **Axios**: HTTP client
- **Lucide React**: Icon library

See `pyproject.toml` for the complete list.

## Development

### Adding New Dependencies

```bash
# Add a new package
uv add package-name

# Add a development dependency
uv add --dev package-name
```

### Updating Dependencies

```bash
# Update all dependencies
uv sync --upgrade

# Update a specific package
uv add package-name --upgrade
```

### Running Tests

```bash
# Activate environment first
source .venv/bin/activate

# Run your tests
python -m pytest
```

## API Configuration

The agents use the following APIs:

- **Gemini API**: Used for the AI models (Gemini 2.5 Flash for text analysis, Gemini 2.5 Flash Image for virtual try-on)
- **Serper API**: Used for web search functionality

Both API keys should be configured in your `.env` file as shown in the setup section.

**API Key Usage:**
- `GOOGLE_API_KEY` (or `GOOGLE_API_KEY_1`): Used by all agents
- For better rate limit handling, you can configure multiple keys (KEY_1, KEY_2, KEY_3)

## Troubleshooting

### Virtual Environment Issues

If you encounter issues with the virtual environment:

```bash
# Remove existing environment
rm -rf .venv

# Recreate with uv sync
uv sync
```

### API Key Issues

- Verify your `.env` file is in the project root
- Check that API keys are valid and have proper permissions
- Ensure `python-dotenv` is loading the environment variables

### Dependency Conflicts

```bash
# Clear cache and reinstall
uv cache clean
uv sync --reinstall
```

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]
