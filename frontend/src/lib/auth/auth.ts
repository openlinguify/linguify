// lib/auth/auth.ts
import { getSession } from '@auth0/nextjs-auth0';
import { NextApiRequest, NextApiResponse } from 'next';

export async function checkAuth(
  req: NextApiRequest,
  res: NextApiResponse
): Promise<boolean> {
  try {
    const session = await getSession(req, res);
    return !!session?.user;
  } catch (error) {
    console.error('Error checking auth:', error);
    return false;
  }
}

export async function getUser(
  req: NextApiRequest,
  res: NextApiResponse
) {
  try {
    const session = await getSession(req, res);
    return session?.user || null;
  } catch (error) {
    console.error('Error getting user:', error);
    return null;
  }
}

export function withAuth(handler: any) {
  return async (req: NextApiRequest, res: NextApiResponse) => {
    const isAuthenticated = await checkAuth(req, res);
    
    if (!isAuthenticated) {
      return res.status(401).json({ error: 'Unauthorized' });
    }
    
    return handler(req, res);
  };
}

// Utilitaire pour vérifier les rôles si nécessaire
export function hasRole(user: any, role: string): boolean {
  return user?.['https://your-namespace/roles']?.includes(role) || false;
}