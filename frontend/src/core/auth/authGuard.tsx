import { NextRequest, NextResponse } from 'next/server';
import { getSession } from '@auth0/nextjs-auth0';

interface HandlerFunction {
  (req: NextRequest, session: Record<string, unknown>): Promise<NextResponse>;
}

export function withProtectedApi(handler: HandlerFunction) {
  return async function (req: NextRequest) {
    try {
      const session = await getSession();

      if (!session?.user) {
        return NextResponse.json(
          { error: 'Unauthorized' },
          { status: 401 }
        );
      }

      // Rate limiting check (implement as needed)
      if (await isRateLimited(req, session.user)) {
        return NextResponse.json(
          { error: 'Too many requests' },
          { status: 429 }
        );
      }

      // CSRF protection (implement as needed)
      if (!(await validateCsrf(req))) {
        return NextResponse.json(
          { error: 'Invalid CSRF token' },
          { status: 403 }
        );
      }

      return await handler(req, session);

    } catch (error) {
      console.error('Protected API error:', error);
      return NextResponse.json(
        { error: 'Internal server error' },
        { status: 500 }
      );
    }
  };
}

async function isRateLimited(
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  req: NextRequest, 
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  user: Record<string, unknown>
): Promise<boolean> {
  // Implement rate limiting logic here
  return false;
}

async function validateCsrf(
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  req: NextRequest
): Promise<boolean> {
  // Implement CSRF validation logic here
  return true;
}

// Example usage:
export const GET = withProtectedApi(async (req, session) => {
  // Your protected API logic here
  return NextResponse.json({ 
    message: 'Protected data',
    user: session.user 
  });
});