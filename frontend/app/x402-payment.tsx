'use client';

import { useRouter } from 'next/navigation';
import { Wallet, ArrowLeft, Terminal } from 'lucide-react';
import axios from 'axios';

export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://fashnai-api.onrender.com';

// Listed x402 prices (keep in sync with backend/x402_config.py)
export const ENDPOINT_PRICES: Record<string, string> = {
  '/api/prices': '$0.02',
  '/api/reviews': '$0.02',
  '/api/specs': '$0.02',
  '/api/search': '$0.05',
  '/api/virtual-tryon': '$0.05',
};

interface PaymentInfo {
  price: string;
  endpoint: string;
  payTo: string | null;
  network: string | null;
}

/**
 * Detect a 402 payment-required response from the x402 middleware and
 * extract the payment details sent back by the server.
 */
export function isPaymentRequired(err: any): PaymentInfo | null {
  if (err?.response?.status !== 402) return null;
  const data = err.response.data || {};
  const endpoint = err.response.config?.url?.split(API_URL)[1] || '';
  const base = endpoint.split('?')[0];
  return {
    price: data.price || ENDPOINT_PRICES[base] || 'pay-per-use',
    endpoint: data.endpoint || base,
    payTo: data.payTo || null,
    network: data.network || null,
  };
}

export function PaymentRequiredPanel({ payment }: { payment: PaymentInfo }) {
  const router = useRouter();
  const cmd = `uv run backend/demo_client.py ${payment.endpoint} <product-url>`;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center px-4">
      <div className="max-w-xl w-full bg-white rounded-2xl shadow-lg p-8">
        <div className="flex items-center space-x-3 mb-6">
          <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl flex items-center justify-center">
            <Wallet className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Payment Required</h2>
            <p className="text-gray-500 text-sm">x402 micropayments in USDC</p>
          </div>
        </div>

        <div className="bg-blue-50 rounded-xl p-4 mb-6 space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-600">Endpoint</span>
            <span className="font-mono font-semibold text-gray-900">{payment.endpoint}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Price per request</span>
            <span className="font-semibold text-blue-700">{payment.price}</span>
          </div>
          {payment.network && (
            <div className="flex justify-between">
              <span className="text-gray-600">Network</span>
              <span className="font-mono text-gray-900">{payment.network}</span>
            </div>
          )}
          {payment.payTo && (
            <div className="flex justify-between gap-4">
              <span className="text-gray-600 shrink-0">Receiving address</span>
              <span className="font-mono text-xs text-gray-900 truncate">{payment.payTo}</span>
            </div>
          )}
        </div>

        <p className="text-gray-600 text-sm leading-relaxed mb-6">
          FashnAI charges per request, settled on-chain in USDC via the{' '}
          <a
            href="https://www.x402.org"
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 font-semibold hover:underline"
          >
            x402 protocol
          </a>
          . An AI agent pays automatically: it receives the 402, signs a USDC
          transfer authorization, and retries the request.
        </p>

        <div className="bg-gray-900 rounded-xl p-4 mb-6">
          <div className="flex items-center space-x-2 mb-2">
            <Terminal className="w-4 h-4 text-gray-400" />
            <span className="text-gray-400 text-xs font-semibold uppercase tracking-wide">
              Try it with the demo agent
            </span>
          </div>
          <code className="block text-green-400 text-xs font-mono break-all">
            {cmd}
          </code>
          <p className="text-gray-500 text-xs mt-2">
            Fund the demo wallet with Base Sepolia USDC at faucet.circle.com first.
          </p>
        </div>

        <button
          onClick={() => router.push('/')}
          className="flex items-center space-x-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Go Back Home</span>
        </button>
      </div>
    </div>
  );
}