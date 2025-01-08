// frontend/middleware.ts
import { NextResponse } from 'next/server';
import { getSession, withMiddlewareAuthRequired } from '@auth0/nextjs-auth0/edge';
import type { NextRequest } from 'next/server';

// Liste des routes publiques
const PUBLIC_ROUTES = [
  '/test',
  '/api/health',
  '/',
  '/login',
  '/register',
  '/about',
  '/contact',
  '/api/auth/.*'  // Pour les endpoints Auth0
];

// Fonction pour vérifier si une route est publique
const isPublicRoute = (path: string): boolean => {
  return PUBLIC_ROUTES.some(route => {
    if (route.endsWith('.*')) {
      const baseRoute = route.slice(0, -2);
      return path.startsWith(baseRoute);
    }
    return path === route;
  });
};

// Fonction pour vérifier les assets et fichiers statiques
const isStaticFile = (path: string): boolean => {
  return /\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$/.test(path);
};

export async function middleware(request: NextRequest) {
  const path = request.nextUrl.pathname;

  // Permettre l'accès aux fichiers statiques
  if (isStaticFile(path)) {
    return NextResponse.next();
  }

  // Permettre l'accès aux routes publiques
  if (isPublicRoute(path)) {
    return NextResponse.next();
  }

  try {
    // Vérifier la session Auth0
    const session = await getSession();
    
    // Si pas de session et route protégée, rediriger vers login
    if (!session?.user) {
      return NextResponse.redirect(new URL('/login', request.url));
    }

    // Utilisateur authentifié, continuer
    return NextResponse.next();
  } catch (error) {
    console.error('Auth middleware error:', error);
    return NextResponse.redirect(new URL('/login', request.url));
  }
}

export const config = {
  matcher: [
    // Exclure les fichiers statiques sauf si dans les paramètres de recherche
    '/((?!_next|[^?]*\\.(html?|css|js|jpg|jpeg|png|gif|ico|svg|woff2?|ttf)).*)',
    // Toujours exécuter pour les routes API
    '/(api|trpc)(.*)',
  ],
};