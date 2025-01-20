// src/app/api/auth/login/route.ts
import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const returnTo = searchParams.get('returnTo') || '/';

    // Create Auth0 authorization URL
    const auth0Domain = process.env.AUTH0_ISSUER_BASE_URL;
    const clientId = process.env.AUTH0_CLIENT_ID;
    const redirectUri = `${process.env.AUTH0_BASE_URL}/api/auth/callback`;
    
    // Create state parameter with returnTo URL
    const state = Buffer.from(JSON.stringify({ returnTo })).toString('base64');

    const authUrl = new URL(`${auth0Domain}/authorize`);
    authUrl.searchParams.set('response_type', 'code');
    authUrl.searchParams.set('client_id', clientId!);
    authUrl.searchParams.set('redirect_uri', redirectUri);
    authUrl.searchParams.set('scope', 'openid profile email');
    authUrl.searchParams.set('state', state);

    return NextResponse.redirect(authUrl.toString(), { status: 307 });
  } catch (error) {
    console.error('Login error:', error);
    return NextResponse.redirect('/login?error=login_failed', { status: 307 });
  }
}

export const runtime = 'edge';