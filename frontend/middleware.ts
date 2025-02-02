// middleware.ts
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
  '/api/auth/callback'
];

const API_PATHS = [
  '/api/v1/course',
  '/api/v1/revision',
  '/api/v1/chat',
  '/api/v1/task',
  '/api/v1/notebook',
  '/api/v1/flashcard'
];

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Allow public paths
  if (PUBLIC_PATHS.includes(pathname)) {
    return NextResponse.next();
  }

  try {
    const session = await getSession();

    // Not authenticated
    if (!session?.user) {
      // API routes return 401
      if (API_PATHS.some(path => pathname.startsWith(path))) {
        return NextResponse.json(
          { error: 'Unauthorized' },
          { status: 401 }
        );
      }

      // Store the original URL to redirect back after login
      const loginUrl = new URL('/api/auth/login', request.url);
      loginUrl.searchParams.set('returnTo', pathname);
      return NextResponse.redirect(loginUrl);
    }

    // Add user info and token to headers
    const requestHeaders = new Headers(request.headers);
    requestHeaders.set('Authorization', `Bearer ${session.accessToken}`);
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
    '/dashboard/:path*',
    '/api/v1/:path*',
  ],
};