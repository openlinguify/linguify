// frontend/next.config.ts
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // La configuration i18n dans pages router est désactivée car elle n'est pas supportée dans App Router
  // Consultez: https://nextjs.org/docs/app/building-your-application/routing/internationalization

  // Conserver votre configuration CORS existante
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
  }
};

export default nextConfig;