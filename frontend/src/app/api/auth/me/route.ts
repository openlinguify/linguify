// src/app/api/auth/me/route.ts
import { cookies } from 'next/headers';
import { getSession } from '@auth0/nextjs-auth0';
import { NextResponse } from 'next/server';

export async function GET() {
  try {
    // Ensure cookies are awaited
    const cookieStore = cookies();

    // Detailed session retrieval with error logging
    const session = await getSession();

    // Comprehensive authentication check
    if (!session) {
      console.error('No session found');
      return NextResponse.json({ error: 'No active session' }, { status: 401 });
    }

    if (!session.user) {
      console.error('Session exists but no user found', session);
      return NextResponse.json({ error: 'Not authenticated' }, { status: 401 });
    }

    // Validate access token
    if (!session.accessToken) {
      console.error('No access token in session', session);
      return NextResponse.json({ error: 'Missing access token' }, { status: 401 });
    }

    // Detailed backend request with comprehensive error handling
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/me/`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${session.accessToken}`,
        'Content-Type': 'application/json',
      },
      // Remove credentials: 'include' as it's not typically used with Bearer tokens
    });

    // Comprehensive response handling
    if (!response.ok) {
      const errorText = await response.text();
      console.error('Backend response error:', {
        status: response.status,
        statusText: response.statusText,
        body: errorText,
      });

      return NextResponse.json(
        { 
          error: 'Failed to fetch user data', 
          details: errorText,
          status: response.status 
        }, 
        { status: response.status || 500 }
      );
    }

    // Parse and return user data
    const userData = await response.json();
    return NextResponse.json(userData);

  } catch (error) {
    // Comprehensive error logging
    console.error('[/api/auth/me] Detailed Error:', {
      message: error instanceof Error ? error.message : 'Unknown error',
      stack: error instanceof Error ? error.stack : 'No stack trace',
    });

    return NextResponse.json(
      { 
        error: 'Internal authentication error',
        details: error instanceof Error ? error.message : 'Unknown error' 
      },
      { status: 500 }
    );
  }
}