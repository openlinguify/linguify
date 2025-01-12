import { handleAuth, handleLogin, handleCallback } from '@auth0/nextjs-auth0';
import { NextApiRequest, NextApiResponse } from 'next';
import { Session } from '@auth0/nextjs-auth0';

const afterCallback = async (
  req: NextApiRequest,
  res: NextApiResponse,
  session: Session
): Promise<Session> => {
  if (session?.user) {
    session.user = {
      ...session.user,
      roles:
        session.user[`${process.env.AUTH0_ISSUER_BASE_URL}/roles`] || ['user'],
    };
  }
  return session;
};

export const GET = handleAuth({
  callback: async (req: NextApiRequest, res: NextApiResponse) => {
    await handleCallback(req, res, { afterCallback });
  },
  login: handleLogin({
    returnTo: '/apps/revision',
    authorizationParams: {
      response_type: 'code',
      scope: 'openid profile email',
      redirect_uri: `${process.env.AUTH0_BASE_URL}/api/auth/callback`,
    },
  }),
});
