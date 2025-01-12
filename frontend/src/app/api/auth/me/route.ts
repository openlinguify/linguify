// src/app/api/auth/me/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { getSession } from '@auth0/nextjs-auth0/edge';

export async function GET(req: NextRequest) {
  try {
    const res = NextResponse.next();
    const session = await getSession(req, res);
    
    if (!session?.user) {
      return NextResponse.json({ 
        user: null,
        isAuthenticated: false 
      }, { status: 401 });
    }

    // On s'assure d'avoir les rôles
    const roles = session.user[`${process.env.AUTH0_ISSUER_BASE_URL}/roles`] || ['user'];

    return NextResponse.json({
      user: {
        id: session.user.sub,
        email: session.user.email,
        name: session.user.name,
        picture: session.user.picture,
        email_verified: session.user.email_verified,
        roles: roles,
        // Ajoutez d'autres propriétés personnalisées si nécessaire
      },
      isAuthenticated: true
    });
  } catch (error) {
    console.error('Session error:', error);
    return NextResponse.json(
      { error: 'Failed to get user session', details: error },
      { status: 500 }
    );
  }
}