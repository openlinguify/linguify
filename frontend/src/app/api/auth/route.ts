import { NextRequest, NextResponse } from 'next/server';
import { getSession, withApiAuthRequired } from '@auth0/nextjs-auth0';

// Get user session
export async function GET(req: NextRequest) {
  try {
    const session = await getSession();
    
    if (!session?.user) {
      return NextResponse.json({ user: null }, { status: 401 });
    }

    return NextResponse.json({ 
      user: {
        id: session.user.sub,
        email: session.user.email,
        name: session.user.name,
        picture: session.user.picture,
        email_verified: session.user.email_verified,
      }
    });
  } catch (error) {
    console.error('Session error:', error);
    return NextResponse.json(
      { error: 'Failed to get user session' },
      { status: 500 }
    );
  }
}

// Protected route example
export const POST = withApiAuthRequired(async function POST(req: NextRequest) {
  try {
    const session = await getSession();
    
    if (!session?.user) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    // Add your protected route logic here
    return NextResponse.json({
      message: 'Protected route accessed successfully',
      user: session.user
    });
  } catch (error) {
    console.error('Protected route error:', error);
    return NextResponse.json(
      { error: 'Failed to process protected route' },
      { status: 500 }
    );
  }
});