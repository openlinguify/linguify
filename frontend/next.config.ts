// Minimal Next.js configuration
import type { NextConfig } from "next";

// Environment validation
const validateEnvironment = () => {
  const requiredEnvVars = [
    'NEXT_PUBLIC_SUPABASE_URL',
    'NEXT_PUBLIC_SUPABASE_ANON_KEY'
  ];

  const missingVars = requiredEnvVars.filter(envVar => {
    const value = process.env[envVar];
    return !value || value.includes('your_supabase') || value === 'undefined';
  });

  if (missingVars.length > 0) {
    console.warn('⚠️  Missing or invalid environment variables:', missingVars);
    console.warn('⚠️  Application will run in fallback mode without authentication');
    console.warn('⚠️  Please set these variables in your .env.local file or deployment environment');
  } else {
    console.log('✅ All required environment variables are set');
  }
};

// Run validation
validateEnvironment();

const nextConfig: NextConfig = {
  // Configuration for external images
  images: {
    remotePatterns: [
      {
        protocol: 'http',
        hostname: 'localhost',
        port: '8000',
        pathname: '/media/**',
      },
      {
        protocol: 'http',
        hostname: '127.0.0.1',
        port: '8000',
        pathname: '/media/**',
      },
      // Production backend on Render
      {
        protocol: 'https',
        hostname: 'linguify-h47a.onrender.com',
        pathname: '/media/**',
      },
      // Supabase Storage
      {
        protocol: 'https',
        hostname: '*.supabase.co',
        pathname: '/storage/v1/object/public/**',
      },
    ],
  },
  
  // Remove all experimental features and webpack customizations temporarily
  async headers() {
    return [
      {
        source: '/api/:path*',
        headers: [
          { key: 'Access-Control-Allow-Credentials', value: 'true' },
          { key: 'Access-Control-Allow-Origin', value: 'https://linguify-h47a.onrender.com' },
          { key: 'Access-Control-Allow-Methods', value: 'GET,OPTIONS,PATCH,DELETE,POST,PUT' },
          { key: 'Access-Control-Allow-Headers', value: 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version, Authorization' },
        ],
      },
    ]
  },

  async rewrites() {
    const isDevelopment = process.env.NODE_ENV === 'development'
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    
    return [
      {
        source: '/api/:path*',
        destination: `${backendUrl}/api/:path*`
      },
      {
        source: '/media/:path*',
        destination: `${backendUrl}/media/:path*`
      }
    ]
  },
};

export default nextConfig;