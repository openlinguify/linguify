import { NextResponse } from 'next/server';
import { getSession, withMiddlewareAuthRequired } from '@auth0/nextjs-auth0/edge';
import type { NextRequest } from 'next/server';

// Types
type Role = 'admin' | 'teacher' | 'premium' | 'user';

interface ProtectedRoute {
  path: string;
  roles: Role[];
}

// Constants
const PUBLIC_ROUTES = [
  '/test',
  '/api/health',
  '/',
  '/login',
  '/register',
  '/about',
  '/contact',
  '/unauthorized',
  '/api/auth/.*',
] as const;

const PROTECTED_ROUTES: ProtectedRoute[] = [
  { path: '/admin', roles: ['admin'] },
  { path: '/teacher', roles: ['teacher', 'admin'] },
  { path: '/premium', roles: ['premium', 'admin'] },
  { path: '/dashboard', roles: ['user', 'admin', 'teacher', 'premium'] }
];

const STATIC_PATTERNS = [
  '_next',
  'images',
  'fonts',
  'favicon.ico',
  'robots.txt',
  'sitemap.xml'
];

// Helper functions
const isPublicRoute = (path: string): boolean => {
  return PUBLIC_ROUTES.some(route => {
    if (route.endsWith('.*')) {
      return path.startsWith(route.slice(0, -2));
    }
    return path === route;
  });
};

const isStaticFile = (path: string): boolean => {
  // Check if path starts with any static pattern
  if (STATIC_PATTERNS.some(pattern => path.startsWith(`/${pattern}`))) {
    return true;
  }
  
  // Check file extensions
  return /\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$/i.test(path);
};

const hasRequiredRole = (userRoles: Role[], path: string): boolean => {
  const matchedRoute = PROTECTED_ROUTES.find(route => path.startsWith(route.path));
  
  if (!matchedRoute) {
    return true; // If no specific roles are required, allow access
  }

  return matchedRoute.roles.some(role => userRoles.includes(role));
};

const getRedirectUrl = (request: NextRequest, path: string): string => {
  const url = new URL(path, request.url);
  url.searchParams.set('returnTo', request.nextUrl.pathname);
  return url.toString();
};

// Middleware
export const middleware = withMiddlewareAuthRequired(async function middleware(
  request: NextRequest
) {
  const path = request.nextUrl.pathname;

  // Allow static files and public routes
  if (isStaticFile(path) || isPublicRoute(path)) {
    return NextResponse.next();
  }

  try {
    const session = await getSession();
    
    // Handle unauthenticated users
    if (!session?.user) {
      return NextResponse.redirect(
        getRedirectUrl(request, '/login')
      );
    }

    // Get user roles from Auth0 custom claims
    const userRoles = (session.user['https://your-namespace/roles'] || ['user']) as Role[];
    
    // Check role-based access
    if (!hasRequiredRole(userRoles, path)) {
      return NextResponse.redirect(
        getRedirectUrl(request, '/unauthorized')
      );
    }

    // Add user info to request headers
    const requestHeaders = new Headers(request.headers);
    requestHeaders.set('x-user-id', session.user.sub);
    requestHeaders.set('x-user-roles', userRoles.join(','));

    // Continue with added context
    return NextResponse.next({
      request: {
        headers: requestHeaders,
      },
    });

  } catch (error) {
    console.error('Auth middleware error:', error);
    // Log detailed error info but don't expose it to the client
    return NextResponse.redirect(
      getRedirectUrl(request, '/login')
    );
  }
});

// Matcher configuration
export const config = {
  matcher: [
    // Match all paths except Next.js specific ones and static files
    '/((?!_next/static|_next/image|favicon.ico).*)',
  ],
};