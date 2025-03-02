// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const PUBLIC_PATHS = [
  '/',
  '/home',
  '/features',
  '/pricing',
  '/company',
  '/contact',
  '/login',
  '/callback',
  '/register',
  '/api/auth/callback',
  '/api/auth/login'
];

// Chemins qui nécessitent une authentification
const PROTECTED_PATHS = [
  '/',
  '/learning',
  '/chat',
  '/progress',
  '/task',
  '/settings',
  // Ajoutez d'autres chemins protégés ici
];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const token = request.cookies.get('access_token');

  // Permettre l'accès aux ressources statiques et chemins publics
  if (
    pathname.startsWith('/_next') ||
    pathname.startsWith('/static') ||
    pathname.startsWith('/api/auth') ||
    PUBLIC_PATHS.some(path => pathname === path || pathname.startsWith(path))
  ) {
    return NextResponse.next();
  }

  // Rediriger vers login si non authentifié et essaie d'accéder à une page protégée
  if (!token && PROTECTED_PATHS.some(path => pathname === path || pathname.startsWith(path))) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  // Rediriger login vers /dashboard si déjà authentifié
  if (pathname === '/login' && token) {
    return NextResponse.redirect(new URL('/', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    '/((?!_next/static|_next/image|favicon.ico).*)',
  ],
};