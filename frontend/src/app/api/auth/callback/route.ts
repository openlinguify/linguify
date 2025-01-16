// src/app/api/auth/callback/route.ts
import { NextResponse } from 'next/server';
import { cookies } from 'next/headers';

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const code = searchParams.get('code');
    const state = searchParams.get('state');
    
    if (!code || !state) {
      return NextResponse.redirect('/login?error=missing_params', { status: 307 });
    }

    // Échanger le code contre des tokens
    const tokenResponse = await fetch(`${process.env.AUTH0_ISSUER_BASE_URL}/oauth/token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        grant_type: 'authorization_code',
        client_id: process.env.AUTH0_CLIENT_ID,
        client_secret: process.env.AUTH0_CLIENT_SECRET,
        code,
        redirect_uri: `${process.env.AUTH0_BASE_URL}/api/auth/callback`
      })
    });

    if (!tokenResponse.ok) {
      const error = await tokenResponse.text();
      console.error('Token error:', error);
      throw new Error(`Failed to exchange code for tokens: ${error}`);
    }

    const tokens = await tokenResponse.json();
    console.log('Tokens received:', { access_token: '...', expires_in: tokens.expires_in });

    // Obtenir les infos utilisateur
    const userResponse = await fetch(`${process.env.AUTH0_ISSUER_BASE_URL}/userinfo`, {
      headers: { 'Authorization': `Bearer ${tokens.access_token}` }
    });

    if (!userResponse.ok) {
      const error = await userResponse.text();
      console.error('User info error:', error);
      throw new Error(`Failed to get user info: ${error}`);
    }

    const user = await userResponse.json();
    console.log('User info received:', { sub: user.sub, email: user.email });

    // Obtenir l'URL de retour depuis state
    let returnTo = '/';
    try {
      const stateData = JSON.parse(Buffer.from(state, 'base64').toString());
      if (stateData.returnTo) {
        returnTo = stateData.returnTo;
      }
    } catch (error) {
      console.error('Error parsing state:', error);
    }

    // Créer la réponse avec redirection
    const response = NextResponse.redirect(new URL(returnTo, request.url));

    // Set cookie with better security options
    const cookieStore = await cookies();
    const sessionData = JSON.stringify({
      user,
      accessToken: tokens.access_token,
      idToken: tokens.id_token,
      expiresAt: Date.now() + (tokens.expires_in * 1000)
    });

    cookieStore.set({
      name: 'session',
      value: sessionData,
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      path: '/',
      maxAge: tokens.expires_in,
      priority: 'high'
    });

    console.log('Session cookie set successfully');
    
    return response;
  } catch (error) {
    console.error('Callback error:', error);
    return NextResponse.redirect('/login?error=' + encodeURIComponent(error.message), {
      status: 307
    });
  }
}

export const runtime = 'edge';