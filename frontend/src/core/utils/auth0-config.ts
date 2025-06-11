// src/utils/auth0-config.ts
import { ConfigParameters } from '@auth0/nextjs-auth0/edge';

export const auth0Config: ConfigParameters = {
  auth0Logout: true,
  clientID: process.env.AUTH0_CLIENT_ID!,
  clientSecret: process.env.AUTH0_CLIENT_SECRET!,
  baseURL: process.env.AUTH0_BASE_URL!,
  issuerBaseURL: process.env.AUTH0_ISSUER_BASE_URL!,
  authorizationParams: {
    scope: 'openid profile email offline_access',
  },
  routes: {
    callback: '/api/auth/callback',
    login: '/api/auth/login',
    postLogoutRedirect: '/',
  },
  session: {
    absoluteDuration: 24 * 60 * 60, // 24 hours in seconds
    name: 'appSession',
    cookie: {
      domain: process.env.NODE_ENV === 'production' 
        ? process.env.AUTH0_COOKIE_DOMAIN 
        : 'localhost',
      httpOnly: true,
      path: '/',
      sameSite: 'lax',
      secure: process.env.NODE_ENV === 'production',
    },
  },
};