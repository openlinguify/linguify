"use client";

import { useAuth0 } from "@auth0/auth0-react";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { storeAuthData } from "@/lib/auth";

// Logger function
const logCallback = (message: string, data?: any) => {
  if (data) {
    console.log(`🔄 CALLBACK: ${message}`, data);
  } else {
    console.log(`🔄 CALLBACK: ${message}`);
  }
};

// Error logger
const logCallbackError = (message: string, error?: any) => {
  console.error(`❌ CALLBACK ERROR: ${message}`, error);
};

export default function CallbackPage() {
  const router = useRouter();
  const { isLoading, isAuthenticated, getAccessTokenSilently, user } = useAuth0();
  const [isHandlingRedirect, setIsHandlingRedirect] = useState(true);

  useEffect(() => {
    async function handleRedirect() {
      try {
        logCallback("Processing Auth0 redirect");
        logCallback("Auth0 State", { isLoading, isAuthenticated, hasUser: !!user });

        // Attendre que Auth0 ait fini de charger
        if (isLoading) {
          logCallback("Auth0 still loading, waiting...");
          return;
        }

        // Si l'authentification a réussi
        if (isAuthenticated && user) {
          logCallback("Auth0 redirect successful", { user: { 
            sub: user.sub,
            email: user.email,
            name: user.name || user.nickname
          }});

          try {
            // Récupérer le token d'accès
            logCallback("Retrieving access token");
            const auth0Response: any = await getAccessTokenSilently({
              authorizationParams: {
                audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE,
                scope: "openid profile email"
              }
            });
            
            // Examiner la réponse d'Auth0
            const tokenType = typeof auth0Response;
            logCallback("Access token retrieved", { 
              tokenType, 
              isObject: tokenType === 'object',
              tokenLength: tokenType === 'string' ? auth0Response.length : 'N/A' 
            });

            // Extraire le token approprié en fonction du format de réponse
            let accessToken: string | undefined;

            if (typeof auth0Response === 'string') {
              accessToken = auth0Response;
            } else {
              accessToken = auth0Response.accessToken || 
                            auth0Response.access_token || 
                            auth0Response.idToken || 
                            auth0Response.id_token || 
                            auth0Response.token;
            }
            
            // Si la réponse est un objet, extraire le token
            if (typeof auth0Response === 'object' && auth0Response !== null) {
              logCallback("Auth0 response is an object", { 
                keys: Object.keys(auth0Response) 
              });
              
              // Tenter d'extraire le token selon différents formats possibles
              accessToken = auth0Response.accessToken || 
                           auth0Response.access_token || 
                           auth0Response.idToken || 
                           auth0Response.id_token || 
                           auth0Response.token;
                           
              if (!accessToken) {
                logCallbackError("Could not extract token from Auth0 response object", auth0Response);
                // Utiliser la réponse entière comme fallback
                accessToken = auth0Response;
              } else {
                logCallback("Successfully extracted token from Auth0 response", {
                  tokenType: typeof accessToken,
                  tokenLength: typeof accessToken === 'string' ? accessToken.length : 'N/A'
                });
              }
            }

            // Formatter les données utilisateur depuis Auth0
            const formattedUser = {
              id: user.sub || '',
              email: user.email || '',
              name: user.name || user.nickname || '',
              picture: user.picture || '',
            };
            logCallback("Formatted user data", formattedUser);

            // Stocker le token et les données utilisateur
            logCallback("Storing authentication data in localStorage");
            if (accessToken) {
              storeAuthData(accessToken, formattedUser);
            } else {
              logCallbackError("Access token is undefined");
              router.push('/login?error=token_error');
            }

            // Rediriger vers la page d'origine ou par défaut
            const returnTo = localStorage.getItem('auth0_return_to') || '/';
            logCallback("Redirecting to original page", { returnTo });
            localStorage.removeItem('auth0_return_to');
            
            // Délai court pour s'assurer que le localStorage est bien sauvegardé
            setTimeout(() => {
              logCallback("Executing redirect");
              router.push(returnTo);
            }, 100);
          } catch (tokenError) {
            logCallbackError("Failed to retrieve access token", tokenError);
            router.push('/login?error=token_error');
          }
        } else if (!isLoading) {
          // Si l'authentification a échoué et que Auth0 a fini de charger
          logCallbackError("Auth0 authentication failed", { isAuthenticated, hasUser: !!user });
          router.push('/login?error=authentication_failed');
        }
      } catch (error) {
        logCallbackError("Error handling Auth0 redirect", error);
        router.push('/login?error=redirect_error');
      } finally {
        setIsHandlingRedirect(false);
      }
    }

    handleRedirect();
  }, [isLoading, isAuthenticated, getAccessTokenSilently, user, router]);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center">
      <div className="text-center">
        <h1 className="text-2xl font-bold mb-4">Connexion en cours...</h1>
        <p className="text-gray-500">Vous allez être redirigé dans un instant.</p>
        <div className="mt-4 text-sm text-gray-400">
          État: {isLoading ? "Chargement..." : isAuthenticated ? "Authentifié" : "Non authentifié"}
        </div>
        {!isLoading && !isAuthenticated && (
          <p className="text-red-500 mt-4">
            Échec de l'authentification. Redirection...
          </p>
        )}
      </div>
    </div>
  );
}