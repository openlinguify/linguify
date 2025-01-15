import { handleAuth, handleCallback } from '@auth0/nextjs-auth0';
import { NextApiRequest, NextApiResponse } from 'next';
import { Session } from '@auth0/nextjs-auth0';

// Fonction pour gérer afterCallback
const afterCallback = async (
  req: NextApiRequest,
  res: NextApiResponse,
  session: Session
): Promise<Session> => {
  if (session?.user) {
    session.user = {
      ...session.user,
      roles: session.user[`${process.env.AUTH0_ISSUER_BASE_URL}/roles`] || ['user'],
    };
  }
  return session;
};

// Handler principal
export default handleAuth({
  callback: handleCallback({
    afterCallback,
  }),
});
