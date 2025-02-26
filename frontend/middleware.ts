// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const PUBLIC_PATHS = [
  '/',
  '/login',
  '/register',
  '/callback',
  '/about',
  '/terms',
  '/privacy',
  '/contact',
  '/api/auth/login',
  '/api/auth/callback',
];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const token = request.cookies.get('access_token');

  // Permettre l'accès aux ressources statiques et chemins publics
  if (
    pathname.startsWith('/_next') ||
    pathname.startsWith('/static') ||
    pathname.startsWith('/api/auth') ||
    PUBLIC_PATHS.some(path => pathname.startsWith(path))
  ) {
    return NextResponse.next();
  }

  // Rediriger vers login si non authentifié
  if (!token && !pathname.startsWith('/login')) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  // Rediriger dashboard vers home si authentifié
  if (pathname === '/dashboard' && token) {
    return NextResponse.redirect(new URL('/', request.url));
  }

  // Rediriger login vers home si déjà authentifié
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