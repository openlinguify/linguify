import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { getSession } from '@auth0/nextjs-auth0';

const PUBLIC_PATHS = [
  '/',
  '/login',
  '/register',
  '/about',
  '/api/auth/login',
  '/api/auth/logout',
  '/api/auth/callback',
];

const STATIC_PATHS = [
  '/_next',
  '/favicon.ico',
  '/images',
  '/fonts',
];

export async function withAuth(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Allow static files and public paths
  if (STATIC_PATHS.some(path => pathname.startsWith(path)) || 
      PUBLIC_PATHS.includes(pathname)) {
    return NextResponse.next();
  }

  try {
    const session = await getSession();

    if (!session?.user) {
      // Store the original URL to redirect back after login
      const loginUrl = new URL('/api/auth/login', request.url);
      loginUrl.searchParams.set('returnTo', pathname);
      
      return NextResponse.redirect(loginUrl);
    }

    // Add user info to request headers for downstream use
    const requestHeaders = new Headers(request.headers);
    requestHeaders.set('x-user-id', session.user.sub);
    requestHeaders.set('x-user-email', session.user.email);

    return NextResponse.next({
      request: {
        headers: requestHeaders,
      },
    });

  } catch (error) {
    console.error('Auth middleware error:', error);
    return NextResponse.redirect(new URL('/api/auth/login', request.url));
  }
}

export const config = {
  matcher: [
    '/((?!api/auth/|_next/|favicon.ico).*)',
  ],
};