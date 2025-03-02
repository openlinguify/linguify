// src/app/api/auth/me/route.ts
import { NextResponse } from 'next/server';
import { cookies } from 'next/headers';

export async function GET(request: Request) {
  try {
    // Get token from authorization header or cookies
    const authHeader = request.headers.get('Authorization');
    
    // Correctly access cookies in Next.js App Router
    const cookieStore = await cookies();
    const cookieToken = cookieStore.get('access_token')?.value;
    
    const token = authHeader?.startsWith('Bearer ') 
      ? authHeader.split(' ')[1] 
      : cookieToken;
    
    if (!token) {
      return NextResponse.json(
        { error: 'No authentication token found' }, 
        { status: 401 }
      );
    }
    
    // Forward request to backend
    const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/auth/me/`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    if (!response.ok) {
      return NextResponse.json(
        { error: `Backend returned ${response.status}` }, 
        { status: response.status }
      );
    }
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('API route error:', error);
    return NextResponse.json(
      { error: 'Internal server error' }, 
      { status: 500 }
    );
  }
}