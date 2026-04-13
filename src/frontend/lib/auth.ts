import { Amplify } from 'aws-amplify';
import { fetchAuthSession, getCurrentUser, signIn, signOut } from 'aws-amplify/auth';
import type { UserContext } from './types';

export function configureAmplify() {
  Amplify.configure({
    Auth: {
      Cognito: {
        userPoolId: process.env.NEXT_PUBLIC_COGNITO_USER_POOL_ID!,
        userPoolClientId: process.env.NEXT_PUBLIC_COGNITO_CLIENT_ID!,
      },
    },
  });
}

export async function getAccessToken(): Promise<string> {
  const session = await fetchAuthSession();
  const token = session.tokens?.accessToken?.toString();
  if (!token) throw new Error('No access token available');
  return token;
}

export async function getCurrentUserContext(): Promise<UserContext | null> {
  try {
    const user = await getCurrentUser();
    const session = await fetchAuthSession();
    const payload = session.tokens?.accessToken?.payload ?? {};
    const groups = (payload['cognito:groups'] as string[]) ?? [];
    // Primary role is the first group (highest privilege)
    const role = groups[0] ?? 'unknown';

    return {
      sub: String(payload.sub ?? user.username),
      email: String(payload.email ?? ''),
      role,
      groups,
    };
  } catch {
    return null;
  }
}

export async function handleSignIn(username: string, password: string) {
  return signIn({ username, password });
}

export async function handleSignOut() {
  return signOut();
}

export function isReadOnly(role: string): boolean {
  return role === 'finance' || role === 'leadership';
}

export function canApprove(role: string): boolean {
  return role === 'finops-analyst' || role === 'engineering-manager';
}
