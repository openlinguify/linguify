import { NextRequest, NextResponse } from 'next/server';
import { getSession, withApiAuthRequired } from '@auth0/nextjs-auth0';

export async function GET(req: NextRequest) {
  try {
    const session = await getSession();
    return NextResponse.json({ user: session?.user || null });
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to get user session' },
      { status: 500 }
    );
  }
}

// Exemple de route protégée
export const POST = withApiAuthRequired(async function POST(req: NextRequest) {
  try {
    const session = await getSession();
    // Logique pour les routes protégées
    return NextResponse.json({ message: 'Protected route accessed successfully' });
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to process protected route' },
      { status: 500 }
    );
  }
});