// frontend/next.config.ts
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Temporarily disable ESLint during build
  eslint: {
    ignoreDuringBuilds: true,
  },
  // Performance optimizations
  images: {
    domains: ['localhost', 'api.linguify.app'],
    formats: ['image/avif', 'image/webp'],
  },
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },
  // Keep experimental features minimal to avoid conflicts
  experimental: {
    optimizeCss: false,
  },
  // Temporarily disable modularizeImports to fix webpack error
  // modularizeImports: {
  //   'lucide-react': {
  //     transform: 'lucide-react/dist/esm/icons/{{member}}'
  //   },
  // },
  
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
  
  // Simplified webpack config to fix errors
  webpack: (config, { dev, isServer }) => {
    // Bundle analyzer - only in build mode
    if (!isServer && process.env.ANALYZE === 'true') {
      const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');
      config.plugins.push(
        new BundleAnalyzerPlugin({
          analyzerMode: 'static',
          openAnalyzer: false,
          reportFilename: '../bundle-analysis.html'
        })
      );
    }
    
    // Simpler chunk optimization
    if (!dev) {
      config.optimization = {
        ...config.optimization,
        splitChunks: {
          chunks: 'all',
          cacheGroups: {
            framework: {
              name: 'framework',
              test: /[\\/]node_modules[\\/](react|react-dom|next)[\\/]/,
              priority: 40,
            },
            commons: {
              name: 'commons',
              minChunks: 3,
              priority: 20,
            },
          },
        },
      };
    }
    
    return config;
  },
};

export default nextConfig;