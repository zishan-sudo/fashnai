"""Demo x402 agent client for the FashnAI API.

Acts as an autonomous agent that pays USDC per API call:
1. Calls the API without payment
2. Receives a 402 with payment requirements
3. Signs a USDC transfer authorization (EIP-3009, no gas needed)
4. Retries with the payment header; facilitator verifies + settles on-chain
5. Prints the settlement result (tx hash, payer, amount)

Usage:
    uv run backend/demo_client.py /api/specs https://www.thenorthface.com/de-de/p/herren-211701/limbara-isolierjacke-fur-herren-NF0A89EG?color=JK3&size=M

Needs EVM_PRIVATE_KEY in .env, funded with Base Sepolia USDC
(faucet: https://faucet.circle.com). TESTNET ONLY.
"""

import asyncio
import json
import os
import sys

from dotenv import load_dotenv
from eth_account import Account

from x402 import x402Client
from x402.http import x402HTTPClient
from x402.http.clients import x402HttpxClient
from x402.mechanisms.evm import EthAccountSigner
from x402.mechanisms.evm.exact.register import register_exact_evm_client

load_dotenv()

# Default: the North Face Limbara jacket used for local testing
DEFAULT_URL = "https://www.thenorthface.com/de-de/p/herren-211701/limbara-isolierjacke-fur-herren-NF0A89EG?color=JK3&size=M"


async def main(endpoint: str, product_url: str) -> None:
    private_key = os.getenv("EVM_PRIVATE_KEY")
    if not private_key:
        print("Error: EVM_PRIVATE_KEY not set in .env")
        sys.exit(1)

    base_url = os.getenv("FASHNAI_API_URL", "http://localhost:8000")
    account = Account.from_key(private_key)

    client = x402Client()
    register_exact_evm_client(client, EthAccountSigner(account))
    http_client = x402HTTPClient(client)

    print(f"Agent wallet: {account.address}")
    print(f"Requesting: POST {base_url}{endpoint}")

    async with x402HttpxClient(client, timeout=300.0) as http:
        response = await http.post(
            f"{base_url}{endpoint}",
            json={"product_url": product_url},
        )
        await response.aread()

        if response.status_code == 402:
            print("\nPayment rejected by facilitator after retry.")
            print("Most likely cause: wallet has no USDC balance.")
            print("Fund the demo wallet with Base Sepolia USDC: https://faucet.circle.com")
            try:
                print("Details:", json.dumps(response.json(), indent=2)[:400])
            except Exception:
                pass
            sys.exit(1)
        if response.status_code != 200:
            print(f"\nFailed: HTTP {response.status_code}")
            print(response.text[:500])
            sys.exit(1)

        print("\n--- RESULT (paid successfully) ---")
        try:
            body = json.loads(response.text)
            print(json.dumps(body, indent=2)[:1200])
        except json.JSONDecodeError:
            print(response.text[:1200])

        try:
            settle = http_client.get_payment_settle_response(
                lambda name: response.headers.get(name)
            )
            data = settle.model_dump()
            print("\n--- PAYMENT SETTLED ---")
            print(f"  payer:   {data.get('payer')}")
            print(f"  network: {data.get('network')}")
            tx = (data.get("transaction") or "")
            print(f"  tx:      {tx}")
            if tx.startswith("0x"):
                print(f"  explorer: https://sepolia.basescan.org/tx/{tx}")
        except ValueError:
            print("\nNo payment settlement header found")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    endpoint = sys.argv[1]
    product_url = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_URL
    asyncio.run(main(endpoint, product_url))