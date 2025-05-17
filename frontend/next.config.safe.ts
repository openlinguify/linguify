// Safe Next.js configuration without experimental features
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Basic performance optimizations
  images: {
    domains: ['localhost', 'api.linguify.app'],
    formats: ['image/avif', 'image/webp'],
  },
  swcMinify: true,
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },
  
  // CORS Headers
  async headers() {
    return [
      {
        source: '/api/auth/:path*',
        headers: [
          { key: 'Access-Control-Allow-Credentials', value: 'true' },
          { key: 'Access-Control-Allow-Origin', value: '*' },
          { key: 'Access-Control-Allow-Methods', value: 'GET,OPTIONS,PATCH,DELETE,POST,PUT' },
          { key: 'Access-Control-Allow-Headers', value: 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version' },
        ],
      },
    ]
  },

  // API Rewrites
  async rewrites() {
    return [
      {
        source: '/api/auth/terms/:path*',
        destination: 'http://localhost:8000/api/auth/terms/:path*'
      },
      {
        source: '/api/auth/:path*',
        destination: 'http://localhost:8000/api/auth/:path*'
      },
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*'
      }
    ]
  },
};

export default nextConfig;