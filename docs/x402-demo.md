# x402 agent payment demo

An AI agent pays FashnAI per request in USDC on Base Sepolia. No API key, no account, no card. The agent gets an HTTP 402, signs a USDC transfer authorization, retries, and receives the result with an on-chain receipt.

## Setup before the demo

1. Start the backend: `uv run backend/api.py` (port 8000).
2. Start the frontend: `cd frontend && npm run dev` (port 3000). It reads `NEXT_PUBLIC_API_URL=http://localhost:8000` from `frontend/.env.local`.
3. Check the agent wallet has USDC. Ask the agent to run `wallet_status`, or fund `EVM_PRIVATE_KEY`'s address at https://faucet.circle.com (Base Sepolia, USDC). The faucet allows one request per two hours and needs a reCAPTCHA click.
4. Open Claude Code in the repo root and approve the `fashnai` MCP server when prompted. Run `/mcp` to confirm it shows as connected.

## Demo flow

1. Show the paywall. Open http://localhost:3000, click the example tile, press Compare. The page shows Payment Required with the price, receiving address and network. This is what an unpaid client sees.
2. Switch to Claude Code and prompt:

   `Check your wallet balance, then get the specs for https://www.thenorthface.com/de-de/p/herren-211701/limbara-isolierjacke-fur-herren-NF0A89EG?color=JK3&size=M`

3. The agent calls `wallet_status`, then `get_product_specs`. The tool result includes a `payment` block with the payer, price, and transaction hash.
4. Open the Basescan link from the result to show the USDC transfer on-chain.
5. Second prompt for a multi-step purchase decision:

   `Compare prices and analyze reviews for the same jacket, then tell me whether it is worth buying and what the total cost of your research was.`

   The agent pays twice ($0.02 each) and reports the spend.

## Talking points

- The server never sees a credential. Payment is the authorization.
- The agent decides to spend. The user sets a wallet and a budget, not a subscription.
- Pricing is per endpoint and lives in `backend/x402_config.py`.
- Settlement happens on Base Sepolia through the public x402 facilitator, so the demo costs nothing.

## Known limits

- The same key is payer and receiver in this demo, so the wallet balance stays flat while the transfers still appear on-chain. Set `X402_PAY_TO` to a different address to show money moving.
- Real product pages take 30 to 90 seconds because the agent crawls and searches live. Run each prompt once beforehand to warm the path, and keep example.com as a fast fallback.
- The browser cannot sign payments. The paying client is the agent.
- The virtual try-on endpoint returns analysis only, with no generated image.

## Other clients

Any MCP client can use the same server. Point it at `uv run --directory <repo> backend/x402_mcp_server.py` over stdio. Gemini CLI and Cursor use the same config shape as `.mcp.json`. ChatGPT cannot sign EIP-3009 authorizations, so it can show the 402 response but cannot pay.
