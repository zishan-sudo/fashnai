"""FashnAI MCP server - lets any MCP client (Claude Code, Claude Desktop,
Cursor, Gemini CLI) act as a paying agent for the FashnAI API.

Each tool calls a paid endpoint of the local API. The x402 HTTP client
handles the protocol transparently: on a 402 response it signs a USDC
transfer authorization (EIP-3009), the facilitator settles on-chain
(Base Sepolia in this demo), and the request is retried. The tool result
includes the settlement details (tx hash, payer) so the agent can narrate
the payment.

Run: uv run backend/x402_mcp_server.py   (stdio transport)
Test: uv run backend/x402_mcp_server.py --selftest <product_url>
"""

import asyncio
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from mcp.server.fastmcp import FastMCP

from eth_account import Account

from x402 import x402Client
from x402.http import x402HTTPClient
from x402.http.clients import x402HttpxClient
from x402.mechanisms.evm import EthAccountSigner
from x402.mechanisms.evm.exact.register import register_exact_evm_client

API_BASE = os.getenv("FASHNAI_API_URL", "http://localhost:8000")

# Listed prices, kept in sync with backend/x402_config.py
PRICES = {
    "/api/specs": "$0.02",
    "/api/prices": "$0.02",
    "/api/reviews": "$0.02",
    "/api/search": "$0.05",
    "/api/virtual-tryon": "$0.05",
}

mcp = FastMCP("fashnai")


def _build_x402_client() -> tuple:
    """Create an x402 client + HTTP helper from EVM_PRIVATE_KEY."""
    private_key = os.getenv("EVM_PRIVATE_KEY")
    if not private_key:
        raise RuntimeError(
            "EVM_PRIVATE_KEY not set - the agent wallet cannot pay. "
            "Add it to .env and fund it with Base Sepolia USDC."
        )
    account = Account.from_key(private_key)
    client = x402Client()
    register_exact_evm_client(client, EthAccountSigner(account))
    return client, x402HTTPClient(client), account


async def _call_paid_api(endpoint: str, payload: dict) -> str:
    """POST to a paid FashnAI endpoint, paying the 402 transparently."""
    client, http_client, account = _build_x402_client()

    async with x402HttpxClient(client, timeout=300.0) as http:
        response = await http.post(f"{API_BASE}{endpoint}", json=payload)
        await response.aread()

        if response.status_code == 402:
            return json.dumps({
                "error": "payment_rejected",
                "message": "Payment failed after retry. Fund the agent wallet "
                           "(see https://faucet.circle.com) and try again.",
                "wallet": account.address,
            })

        if response.status_code != 200:
            return json.dumps({
                "error": f"API returned HTTP {response.status_code}",
                "detail": response.text[:500],
            })

        try:
            body = json.loads(response.text)
        except json.JSONDecodeError:
            body = {"raw": response.text[:2000]}

        settlement = {}
        try:
            settle = http_client.get_payment_settle_response(
                lambda name: response.headers.get(name)
            )
            data = settle.model_dump()
            tx = data.get("transaction") or ""
            settlement = {
                "payment": {
                    "status": "settled on-chain",
                    "price": PRICES.get(endpoint, "unknown"),
                    "payer": data.get("payer"),
                    "network": data.get("network"),
                    "transaction": tx,
                    "explorer": f"https://sepolia.basescan.org/tx/{tx}" if tx.startswith("0x") else None,
                }
            }
        except ValueError:
            settlement = {"payment": {"status": "no settlement header (free response?)"}}

        # Keep the payload compact for the LLM context
        body_str = json.dumps(body)
        if len(body_str) > 4000:
            body = {"summary": body_str[:4000] + "...(truncated)"}

        return json.dumps({**body, **settlement})


@mcp.tool()
async def get_product_specs(product_url: str) -> str:
    """Extract detailed product specifications (brand, material, sizes, features)
    for a fashion product URL. Costs $0.02 USDC, paid automatically on-chain via x402."""
    return await _call_paid_api("/api/specs", {"product_url": product_url})


@mcp.tool()
async def compare_prices(product_url: str) -> str:
    """Find the same product across multiple retailers with prices and availability.
    Costs $0.02 USDC, paid automatically on-chain via x402."""
    return await _call_paid_api("/api/prices", {"product_url": product_url})


@mcp.tool()
async def analyze_reviews(product_url: str) -> str:
    """Analyze customer reviews: rating, sentiment, pros/cons, common themes.
    Costs $0.02 USDC, paid automatically on-chain via x402."""
    return await _call_paid_api("/api/reviews", {"product_url": product_url})


@mcp.tool()
async def full_product_analysis(product_url: str) -> str:
    """Run all three analyses at once: prices, reviews, and specifications.
    Costs $0.05 USDC, paid automatically on-chain via x402."""
    return await _call_paid_api("/api/search", {"product_url": product_url})


@mcp.tool()
async def wallet_status() -> str:
    """Check the agent's USDC balance on Base Sepolia before making paid calls."""
    try:
        client, _, account = _build_x402_client()
    except RuntimeError as e:
        return json.dumps({"error": str(e)})

    import httpx
    usdc = os.getenv("X402_USDC_ADDRESS", "0x036CbD53842c5426634e7929541eC2318f3dCF7e")
    data = "0x70a08231" + "0" * 24 + account.address[2:].lower()
    rpc = os.getenv("BASE_SEPOLIA_RPC", "https://sepolia.base.org")
    r = httpx.post(rpc, json={"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                              "params": [{"to": usdc, "data": data}, "latest"]}, timeout=30)
    try:
        balance = int(r.json()["result"], 16) / 1e6
    except Exception:
        balance = None
    return json.dumps({
        "wallet": account.address,
        "usdc_balance": balance,
        "network": "Base Sepolia (eip155:84532)",
        "note": "Fund at https://faucet.circle.com" if not balance else None,
    })


async def _selftest(product_url: str) -> None:
    print("wallet:", await wallet_status())
    print("specs:", (await get_product_specs(product_url))[:2000])


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
        url = sys.argv[2] if len(sys.argv) > 2 else "https://example.com"
        asyncio.run(_selftest(url))
    else:
        mcp.run(transport="stdio")