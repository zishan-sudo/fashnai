"""x402 payment configuration for the FashnAI API.

Wires the FastAPI app to the x402 protocol so agents pay USDC per request:
- No X-PAYMENT header -> 402 response with payment requirements
- Paid request -> facilitator verifies + settles on-chain, then the route runs

Network, receiving address, and facilitator URL come from env vars
(X402_NETWORK, X402_PAY_TO). Base Sepolia (eip155:84532) is the default so
the demo costs nothing.
"""

import logging
import os

from dotenv import load_dotenv

from x402 import x402ResourceServer
from x402.http import HTTPFacilitatorClient
from x402.http.types import (
    HTTPRequestContext,
    HTTPResponseBody,
    PaymentOption,
    RouteConfig,
)
from x402.mechanisms.evm.exact import ExactEvmServerScheme

load_dotenv()

logger = logging.getLogger(__name__)

# Base Sepolia testnet; override for mainnet (eip155:8453)
X402_NETWORK = os.getenv("X402_NETWORK", "eip155:84532")
# Public Coinbase facilitator verifies and settles payments on-chain
X402_FACILITATOR_URL = os.getenv("X402_FACILITATOR_URL", "https://x402.org/facilitator")

PAY_TO = os.getenv("X402_PAY_TO")

# Per-request prices (USD, settled in USDC)
ROUTES: dict = {
    "POST /api/search": {
        "accepts": {"scheme": "exact", "price": "$0.05", "payTo": "", "network": X402_NETWORK},
        "description": "FashnAI full product analysis (prices + reviews + specs)",
    },
    "POST /api/prices": {
        "accepts": {"scheme": "exact", "price": "$0.02", "payTo": "", "network": X402_NETWORK},
        "description": "FashnAI price comparison across retailers",
    },
    "POST /api/reviews": {
        "accepts": {"scheme": "exact", "price": "$0.02", "payTo": "", "network": X402_NETWORK},
        "description": "FashnAI review analysis and sentiment",
    },
    "POST /api/specs": {
        "accepts": {"scheme": "exact", "price": "$0.02", "payTo": "", "network": X402_NETWORK},
        "description": "FashnAI product specification extraction",
    },
    "POST /api/virtual-tryon": {
        "accepts": {"scheme": "exact", "price": "$0.05", "payTo": "", "network": X402_NETWORK},
        "description": "FashnAI virtual try-on analysis",
    },
}


def _unpaid_body(ctx: HTTPRequestContext) -> HTTPResponseBody:
    """JSON body for 402 responses so browsers (not just agents) can read them."""
    route = None
    for key, cfg in ROUTES.items():
        if key.endswith(ctx.path):
            route = cfg
            break
    accepts = route["accepts"] if route else {}
    return HTTPResponseBody(
        content_type="application/json",
        body={
            "error": "Payment required",
            "endpoint": ctx.path,
            "price": accepts.get("price"),
            "payTo": PAY_TO,
            "network": accepts.get("network"),
            "hint": "Pay via x402 protocol - see backend/demo_client.py",
        },
    )


def build_routes_and_server() -> tuple[dict, "x402ResourceServer"]:
    """Return (routes, server) for app.add_middleware(PaymentMiddlewareASGI, ...).

    Raises RuntimeError if X402_PAY_TO is not configured.
    """
    if not PAY_TO:
        raise RuntimeError("X402_PAY_TO not set - cannot enforce payments")

    routes = {}
    for key, cfg in ROUTES.items():
        routes[key] = RouteConfig(
            accepts=PaymentOption(
                scheme=cfg["accepts"]["scheme"],
                pay_to=PAY_TO,
                price=cfg["accepts"]["price"],
                network=cfg["accepts"]["network"],
            ),
            description=cfg["description"],
            unpaid_response_body=_unpaid_body,
        )

    facilitator = HTTPFacilitatorClient({"url": X402_FACILITATOR_URL})
    server = x402ResourceServer(facilitator)
    server.register("eip155:*", ExactEvmServerScheme())

    return routes, server


def price_for(path: str) -> str:
    """Look up the listed price for an API path (e.g. '/api/specs')."""
    for key, cfg in ROUTES.items():
        if key.endswith(path):
            return cfg["accepts"]["price"]
    return "unknown"