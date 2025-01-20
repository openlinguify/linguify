// src/app/api/auth/me/route.ts
import { NextResponse } from 'next/server';
import { cookies } from 'next/headers';

export async function GET() {
  try {
    // Attendre cookies() et get()
    const cookieStore = await cookies();
    const sessionCookie = cookieStore.get('session');

    if (!sessionCookie?.value) {
      return NextResponse.json(
        { 
          isAuthenticated: false,
          error: 'No session found'
        },
        { status: 401 }
      );
    }

    const session = JSON.parse(sessionCookie.value);
    
    // Vérifier si la session est expirée
    if (Date.now() > session.expiresAt) {
      return NextResponse.json(
        { 
          isAuthenticated: false, 
          error: 'Session expired' 
        },
        { status: 401 }
      );
    }

    // Retourner les infos utilisateur sans données sensibles
    return NextResponse.json({
      isAuthenticated: true,
      user: {
        sub: session.user.sub,
        email: session.user.email,
        name: session.user.name,
        picture: session.user.picture,
      }
    });
  } catch (error) {
    console.error('Error getting user session:', error);
    return NextResponse.json(
      { 
        isAuthenticated: false, 
        error: 'Invalid session' 
      },
      { status: 401 }
    );
  }
}

export const runtime = 'edge';