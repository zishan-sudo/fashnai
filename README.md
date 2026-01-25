# FashnAI

AI-powered fashion research and price comparison system using multi-agent architecture. Specialized in apparel and footwear analysis.

## Features

- **Fashion Price Comparison Agent**: Finds the same fashion product (clothing, shoes, accessories) across multiple fashion e-commerce websites and compares prices

## Prerequisites

- Python 3.13 or higher
- [uv](https://github.com/astral-sh/uv) package manager
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
cd /home/zishan/PycharmProjects/fashnai
```

### 3. Set Up Environment

Create a `.env` file in the project root with the following variables:

```env
GEMINI_API_KEY=your-gemini-api-key
SERPER_API_KEY=your-serper-api-key
```

**Required API Keys:**
- **Gemini API**: Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
- **Serper API**: Get your API key from [serper.dev](https://serper.dev)

### 4. Install Dependencies

Use `uv sync` to create a virtual environment and install all dependencies:

```bash
uv sync
```

This command will:
- Create a virtual environment in `.venv/`
- Install all dependencies specified in `pyproject.toml`
- Lock dependencies for reproducibility


### 5. Activate Virtual Environment

```bash
# On Linux/macOS
source .venv/bin/activate

# On Windows
.venv\Scripts\activate
```


### 6.Setup crawl4ai to install browser tools
```
source .venv/bin/activate
crawl4ai-setup
```

### 7.To Enable debugging
`export AGNO_DEBUG=true`

## Usage

### Fashion Price Comparison Agent

Compare prices for fashion products (apparel, shoes, accessories) across multiple fashion e-commerce websites:

```python
from backend.PriceAgent import compare_prices

# Example with a fashion product URL
result = compare_prices("https://www.asos.com/product/example-dress")
print(result.content)
```


### Activate environment and run playground
- Rename .env-template to .env and set the API Keys
- Is necessary to create an account with agno to use the playground, even locally
```
uv run backend/playground.py
```

Connect to  AgentOS UI for a readymade interface to interact with the agent as mentioend here https://docs.agno.com/introduction

## Project Structure

```
styleiq/
├── backend/
│   ├── ApparelResearchAgent.py  # Apparel fit analysis agent
│   ├── PriceAgent.py            # Fashion price comparison agent
│   └── playground.py            # Testing and experimentation
├── .env                         # Environment variables (not in git)
├── pyproject.toml              # Project dependencies
└── README.md                   # This file
```

## Dependencies

Key dependencies include:
- **agno**: Multi-agent framework
- **google-genai**: Google Gemini AI models
- **crawl4ai**: Web scraping and crawling
- **duckduckgo-search**: Web search functionality
- **google-search-results**: Serper API integration
- **pydantic**: Data validation and schema definition
- **fastapi**: API framework (for future endpoints)

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

- **Gemini API**: Used for the AI model (Gemini 2.0 Flash)
- **Serper API**: Used for web search functionality

Both API keys should be configured in your `.env` file as shown in the setup section.

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
