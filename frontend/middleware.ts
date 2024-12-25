// frontend/middleware.ts
import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";

// Crée un vérificateur pour les routes publiques
const isPublicRoute = createRouteMatcher(["/test"]);

export default clerkMiddleware(async (auth, req) => {
  // Récupérer l'authentification de l'utilisateur
  const { userId } = await auth(); // Résout la promesse

  // Si ce n'est pas une route publique et qu'il n'y a pas d'utilisateur connecté, renvoie une erreur 401
  if (!isPublicRoute(req) && !userId) {
    return new Response("Unauthorized", { status: 401 });
  }
});

export const config = {
  matcher: [
    // Skip Next.js internals and all static files, unless found in search params
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    // Always run for API routes
    '/(api|trpc)(.*)',
  ],
};