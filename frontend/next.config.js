/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  // In production (Vercel), the frontend calls the backend directly via
  // NEXT_PUBLIC_API_URL — no proxy needed. The rewrites below are only
  // active during local development where the backend runs on port 8000.
  async rewrites() {
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

    // On Vercel, NEXT_PUBLIC_API_URL will be set (e.g. https://careeros-api.onrender.com).
    // The Axios client in api.ts already uses that as its baseURL, so requests
    // go directly to the backend. These rewrites are a dev-only fallback.
    if (backendUrl !== 'http://localhost:8000') {
      return []
    }

    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
      {
        source: '/auth/:path*',
        destination: 'http://localhost:8000/auth/:path*',
      },
    ]
  },
}
module.exports = nextConfig
