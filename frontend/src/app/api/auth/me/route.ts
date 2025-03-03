// src/app/api/auth/me/route.ts
import { NextResponse } from 'next/server';
import { cookies } from 'next/headers';

export async function GET(request: Request) {
  // Add debug logging
  console.log('🔍 /api/auth/me route handler called');
  
  try {
    // Get token from authorization header
    const authHeader = request.headers.get('Authorization');
    let token = null;
    
    if (authHeader?.startsWith('Bearer ')) {
      token = authHeader.split(' ')[1];
      console.log('🔑 Found token in Authorization header', { tokenLength: token.length });
    } else {
      console.log('❌ No valid Authorization header found');
    }
    
    // If no token in header, try cookies
    if (!token) {
      const cookieStore = await cookies();
      const cookieToken = cookieStore.get('access_token')?.value;
      
      if (cookieToken) {
        token = cookieToken;
        console.log('🍪 Found token in cookies', { tokenLength: token.length });
      } else {
        console.log('❌ No token found in cookies');
      }
      
      // For debugging - check all available cookies
      const allCookies = cookieStore.getAll();
      console.log('📋 All cookies:', Object.fromEntries(
        allCookies.map(c => [c.name, `${c.value.substring(0, 10)}...`])
      ));
    }
    
    if (!token) {
      console.log('❌ No authentication token found in any source');
      return NextResponse.json(
        { error: 'No authentication token found' }, 
        { status: 401 }
      );
    }
    
    // Forward request to backend
    console.log(`🔄 Forwarding request to ${process.env.NEXT_PUBLIC_BACKEND_URL}/api/auth/me/`);
    const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/auth/me/`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    if (!response.ok) {
      const errorBody = await response.text();
      console.log(`❌ Backend error: ${response.status}`, { errorBody });
      return NextResponse.json(
        { 
          error: `Backend authentication failed`,
          status: response.status,
          details: errorBody
        }, 
        { status: response.status }
      );
    }
    
    const data = await response.json();
    console.log('✅ Auth successful, returning user data');
    return NextResponse.json(data);
  } catch (error) {
    console.error('💥 API route error:', error);
    return NextResponse.json(
      { error: 'Internal server error', details: String(error) }, 
      { status: 500 }
    );
  }
}