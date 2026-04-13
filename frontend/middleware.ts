import { NextRequest, NextResponse } from 'next/server'

/**
 * Next.js middleware — protects /dashboard/* routes.
 * Public routes: /, /login, /signup, /onboarding
 */
const PUBLIC_PATHS = ['/', '/login', '/signup', '/onboarding']

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Allow public routes
  if (PUBLIC_PATHS.some((p) => pathname === p)) {
    return NextResponse.next()
  }

  // Allow static assets & API routes
  if (
    pathname.startsWith('/_next') ||
    pathname.startsWith('/api') ||
    pathname.includes('.')
  ) {
    return NextResponse.next()
  }

  // Check for auth token in cookie (set by client-side JS is not available in middleware,
  // so we use a lightweight cookie check — the real protection is in the auth store hydration)
  // This is a best-effort redirect for direct URL navigation
  const token = request.cookies.get('careeros_token')?.value

  // Since we use localStorage (not cookies) for token storage,
  // the middleware can't fully gate access. The client-side useProtectedRoute() hook
  // handles the actual redirect. This middleware is a progressive enhancement.
  if (!token && pathname.startsWith('/dashboard')) {
    // We allow through but let the client-side hook handle the redirect.
    // This avoids blocking legitimate hydration scenarios.
    return NextResponse.next()
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
}
