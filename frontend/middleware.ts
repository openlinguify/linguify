// src/middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export async function middleware(request: NextRequest) {
  // Skip auth check for public routes
  if (
    request.nextUrl.pathname.startsWith('/_next') ||
    request.nextUrl.pathname.startsWith('/api/auth') ||
    request.nextUrl.pathname === '/login' ||
    request.nextUrl.pathname === '/'
  ) {
    return NextResponse.next();
  }

  // Check for session cookie
  const session = request.cookies.get('session');
  console.log('Checking session:', session ? 'Found' : 'Not found');

  if (!session?.value) {
    console.log('No session found, redirecting to login');
    const returnTo = encodeURIComponent(request.nextUrl.pathname);
    return NextResponse.redirect(
      new URL(`/api/auth/login?returnTo=${returnTo}`, request.url)
    );
  }

  try {
    // Verify session is valid
    const sessionData = JSON.parse(session.value);
    console.log('Session data:', { 
      isExpired: Date.now() > sessionData.expiresAt,
      timeLeft: Math.round((sessionData.expiresAt - Date.now()) / 1000)
    });

    if (Date.now() > sessionData.expiresAt) {
      console.log('Session expired, redirecting to login');
      const returnTo = encodeURIComponent(request.nextUrl.pathname);
      return NextResponse.redirect(
        new URL(`/api/auth/login?returnTo=${returnTo}`, request.url)
      );
    }

    // Add user info to request headers
    const requestHeaders = new Headers(request.headers);
    requestHeaders.set('x-user-id', sessionData.user.sub);
    requestHeaders.set('x-user-email', sessionData.user.email);

    // Clone the response and add the headers
    const response = NextResponse.next({
      request: {
        headers: requestHeaders,
      },
    });

    return response;
  } catch (error) {
    console.error('Session verification error:', error);
    // Invalid session, redirect to login
    return NextResponse.redirect(
      new URL('/api/auth/login', request.url)
    );
  }
}

export const config = {
  matcher: [
    '/apps/:path*',
    '/settings/:path*',
    '/profile/:path*',
    '/api/:path*',
  ]
};