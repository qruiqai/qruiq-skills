import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { getToken } from 'next-auth/jwt';

const PUBLIC_PATHS = ['/', '/api/auth'];

export async function middleware(request: NextRequest) {
  const path = request.nextUrl.pathname;

  if (path.startsWith('/api/auth/callback/')) return NextResponse.next();

  const isPublic = PUBLIC_PATHS.some(p => path === p || path.startsWith(p + '/'));
  if (isPublic || path.startsWith('/api/')) return NextResponse.next();

  const token = await getToken({ req: request, secret: process.env.NEXTAUTH_SECRET });
  if (token) return NextResponse.next();

  const callbackUrl = encodeURIComponent(request.url);
  return NextResponse.redirect(new URL(`/?callbackUrl=${callbackUrl}`, request.url));
}

export const config = {
  matcher: [
    '/dashboard/:path*',
    '/profile/:path*',
    // add more protected routes here
  ],
};
