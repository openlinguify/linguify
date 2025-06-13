import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { getUnauthenticatedRedirect, logEnvironmentInfo } from '@/core/utils/environment';

// Debug function to log detailed information
function debugLog(message: string, details?: Record<string, any>) {
  const timestamp = new Date().toISOString();
  console.log(`🕰️ [${timestamp}] ${message}`);
  
  if (details) {
    console.log('📝 Additional Details:');
    Object.entries(details).forEach(([key, value]) => {
      console.log(`   • ${key}: ${JSON.stringify(value)}`);
    });
  }
  
  console.log('-----------------------------------');
}

// Routes accessibles sans authentification
const PUBLIC_PATHS = [
  '/home',
  '/features',
  '/pricing',
  '/company',
  '/contact',
  '/register',
  '/callback',
  '/api/auth/callback',
  '/api/auth/login',
  '/annexes/terms',
  '/annexes/legal',
  '/annexes/privacy',
];

// Routes qui nécessitent une authentification
const PROTECTED_PATHS = [
  '/',
  '/learning',
  '/chat',
  '/progress',
  '/task',
  '/settings',
  '/notebook',
  '/coaching',
  '/flashcard',
  '/revision',
  '/community'
];

// Routes d'authentification
const AUTH_PATHS = [
  '/login',
  '/register',
  '/callback'
];

// Assets et ressources statiques à ignorer
const STATIC_PATHS = [
  '/_next',
  '/static',
  '/api/auth',
  '/favicon.ico',
  '/logo',
  '/img',
  '/icons'
];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  
  // Log comprehensive request details
  debugLog('🔍 Middleware Intercepted Request', {
    pathname,
    method: request.method,
    host: request.headers.get('host'),
    userAgent: request.headers.get('user-agent'),
    referrer: request.headers.get('referer')
  });

  // Logging all headers
  const headers = Object.fromEntries(request.headers.entries());
  debugLog('🌐 Request Headers', { headers });

  // Detailed cookie logging
  const allCookies = request.cookies.getAll();
  debugLog('🍪 Cookies', { 
    cookieCount: allCookies.length,
    cookies: allCookies.map(cookie => ({
      name: cookie.name, 
      value: cookie.value,
      // Mask sensitive tokens
      maskedValue: cookie.value ? '*'.repeat(Math.min(cookie.value.length, 10)) + '...' : null
    }))
  });

  // Check for specific authentication tokens
  const accessToken = request.cookies.get('access_token');
  const authToken = request.cookies.get('auth_token');
  const sessionToken = request.cookies.get('session');
  
  debugLog('🔐 Authentication Tokens', {
    hasAccessToken: !!accessToken,
    hasAuthToken: !!authToken,
    hasSessionToken: !!sessionToken
  });

  // Check localStorage flag for recent login
  const recentLoginFlag = request.cookies.get('supabase_login_success');
  
  // Check for Supabase auth cookies
  const supabaseAuth = request.cookies.get('sb-access-token') || 
                      request.cookies.get('sb-auth-token') ||
                      request.cookies.get('sb-refresh-token');
  
  // Comprehensive authentication check
  const isAuthenticated = !!(
    accessToken || 
    authToken || 
    sessionToken || 
    supabaseAuth ||
    recentLoginFlag ||
    request.headers.get('Authorization')
  );

  debugLog('🔒 Authentication Status', {
    isAuthenticated,
    authMethods: {
      accessToken: !!accessToken,
      authToken: !!authToken,
      sessionToken: !!sessionToken,
      authHeader: !!request.headers.get('Authorization')
    }
  });

  // Ignore static resources
  if (STATIC_PATHS.some(path => pathname.startsWith(path))) {
    debugLog('📁 Static Resource', { 
      action: 'Allow Access',
      reason: 'Matches static path pattern'
    });
    return NextResponse.next();
  }

  // Root path handling
  if (pathname === '/') {
    // Special handling for production domains
    const host = request.headers.get('host') || '';
    const isProductionDomain = host.includes('openlinguify.com');
    
    // Log domain info for debugging
    debugLog('🌐 Domain Check', {
      host,
      isProductionDomain,
      hostname: request.nextUrl.hostname
    });
    
    if (!isAuthenticated) {
      debugLog('🚪 Root Path', {
        action: 'Redirect',
        reason: 'Unauthenticated',
        destination: '/home',
        domain: host
      });
      return NextResponse.redirect(new URL('/home', request.url));
    }
    
    debugLog('🏠 Root Path', {
      action: 'Allow Access',
      reason: 'Authenticated',
      domain: host
    });
    return NextResponse.next();
  }

  // Authentication paths
  if (AUTH_PATHS.some(path => pathname === path)) {
    if (isAuthenticated) {
      debugLog('🔓 Auth Path', {
        action: 'Redirect',
        reason: 'Already Authenticated',
        destination: '/'
      });
      return NextResponse.redirect(new URL('/', request.url));
    }
    
    debugLog('🔑 Auth Path', {
      action: 'Allow Access',
      reason: 'Not Authenticated'
    });
    return NextResponse.next();
  }

  // Public paths
  if (PUBLIC_PATHS.some(path => pathname === path || pathname.startsWith(path))) {
    debugLog('🌍 Public Path', {
      action: 'Allow Access',
      reason: 'Matches public path pattern'
    });
    return NextResponse.next();
  }

  // Legacy route redirects for /learn/lesson/ routes
  if (pathname.startsWith('/learn/lesson/')) {
    const lessonId = pathname.split('/')[3];
    if (lessonId && !isNaN(Number(lessonId))) {
      const newUrl = new URL(`/learning/content/vocabulary/${lessonId}`, request.url);
      debugLog('🔄 Legacy Route Redirect', {
        action: 'Redirect',
        reason: 'Legacy /learn/lesson/ format',
        from: pathname,
        to: newUrl.pathname
      });
      return NextResponse.redirect(newUrl);
    }
  }

  // Protected paths
  if (PROTECTED_PATHS.some(path => pathname === path || pathname.startsWith(path))) {
    if (!isAuthenticated) {
      const host = request.headers.get('host') || '';
      const redirectDestination = getUnauthenticatedRedirect(host);
      
      // Log environment info for debugging
      logEnvironmentInfo('Middleware', host);
      
      debugLog('🛡️ Protected Path', {
        action: 'Redirect',
        reason: 'Not Authenticated',
        destination: redirectDestination,
        host,
        pathname
      });
      
      return NextResponse.redirect(new URL(redirectDestination, request.url));
    }
    
    debugLog('🔒 Protected Path', {
      action: 'Allow Access',
      reason: 'Authenticated'
    });
    return NextResponse.next();
  }

  // Catch-all for unspecified routes
  debugLog('❓ Unspecified Route', {
    action: 'Allow Access',
    reason: 'No specific routing rule matched'
  });
  return NextResponse.next();
}

export const config = {
  matcher: [
    '/((?!_next/static|_next/image|favicon.ico).*)',
  ],
};