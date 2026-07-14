import { NextRequest, NextResponse } from "next/server";

// Next.js 16 renamed Middleware to Proxy (same functionality, new name/file).
// This only does an optimistic check (does a sessionid cookie exist?) — it
// can't verify the session is actually still valid server-side without an
// extra request, which Proxy shouldn't do. The real authorization check
// happens in Django on every proxied API call; this is just UX-level
// routing so logged-out users land on /login instead of a broken page.

const PUBLIC_PATHS = ["/login"];

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const hasSession = request.cookies.has("sessionid");
  const isPublicPath = PUBLIC_PATHS.includes(pathname);

  if (!hasSession && !isPublicPath) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  if (hasSession && isPublicPath) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|.*\\.svg$).*)"],
};
