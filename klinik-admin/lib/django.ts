import type { IncomingMessage, ServerResponse } from "http";

// Server-only: reads/writes cookies via the raw req/res passed in from
// getServerSideProps or an API route handler. The browser never talks to
// Django directly; it only ever talks to this Next.js server, which forwards
// to Django on its behalf.

const DJANGO_API_URL = process.env.DJANGO_API_URL ?? "http://localhost:8000";

const SAFE_METHODS = new Set(["GET", "HEAD", "OPTIONS", "TRACE"]);

export class DjangoApiError extends Error {
  status: number;
  body: unknown;

  constructor(status: number, body: unknown) {
    super(`Django API request failed with status ${status}`);
    this.name = "DjangoApiError";
    this.status = status;
    this.body = body;
  }
}

// Satisfied by both NextApiRequest and GetServerSidePropsContext["req"].
type ReqLike = Pick<IncomingMessage, "headers">;
// Satisfied by both NextApiResponse and GetServerSidePropsContext["res"].
type ResLike = Pick<ServerResponse, "getHeader" | "setHeader">;

function parseCookieHeader(cookieHeader: string): Record<string, string> {
  const out: Record<string, string> = {};
  for (const part of cookieHeader.split(";")) {
    const eq = part.indexOf("=");
    if (eq === -1) continue;
    out[part.slice(0, eq).trim()] = part.slice(eq + 1).trim();
  }
  return out;
}

/**
 * Calls the Django API server-to-server, forwarding the current request's
 * cookies (sessionid, csrftoken) so the call rides on the same Django
 * session the browser has. Attaches X-CSRFToken automatically for mutating
 * methods, per Django's documented CSRF-for-AJAX pattern.
 */
export async function djangoFetch(req: ReqLike, path: string, init: RequestInit = {}): Promise<Response> {
  const cookieHeader = req.headers.cookie ?? "";

  const headers = new Headers(init.headers);
  headers.set("Cookie", cookieHeader);
  if (init.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const method = (init.method ?? "GET").toUpperCase();
  if (!SAFE_METHODS.has(method)) {
    const csrftoken = parseCookieHeader(cookieHeader).csrftoken;
    if (csrftoken) {
      headers.set("X-CSRFToken", csrftoken);
    }
  }

  return fetch(`${DJANGO_API_URL}${path}`, { ...init, headers, cache: "no-store" });
}

/** djangoFetch, but parses the JSON body and throws DjangoApiError on non-2xx. */
export async function djangoJson<T = unknown>(req: ReqLike, path: string, init: RequestInit = {}): Promise<T> {
  const response = await djangoFetch(req, path, init);
  const body = await response.json().catch(() => null);
  if (!response.ok) {
    throw new DjangoApiError(response.status, body);
  }
  return body as T;
}

/** Appends (does not clobber) a raw Set-Cookie string onto the response. */
export function appendSetCookie(res: ResLike, rawCookie: string): void {
  const existing = res.getHeader("Set-Cookie");
  const existingArr = existing ? (Array.isArray(existing) ? existing.map(String) : [String(existing)]) : [];
  res.setHeader("Set-Cookie", [...existingArr, rawCookie]);
}

/**
 * Relays every Set-Cookie header from a Django response onto the current
 * Next.js response, unparsed — use right after login/logout calls.
 */
export function relayCookies(res: ResLike, djangoResponse: Response): void {
  const setCookieHeaders = djangoResponse.headers.getSetCookie?.() ?? [];
  for (const raw of setCookieHeaders) {
    appendSetCookie(res, raw);
  }
}
