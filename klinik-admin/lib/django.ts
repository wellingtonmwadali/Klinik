import { cookies } from "next/headers";

// Server-only: this module reads/writes the incoming request's cookie jar via
// next/headers, which throws if imported from a Client Component. Never call
// these from "use client" code — the browser should never talk to Django
// directly; it only ever talks to this Next.js server (Server Components /
// Server Actions), which forwards to Django on its behalf.

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

/**
 * Calls the Django API server-to-server, forwarding the current request's
 * cookies (sessionid, csrftoken) so the call rides on the same Django
 * session the browser has. Attaches X-CSRFToken automatically for mutating
 * methods, per Django's documented CSRF-for-AJAX pattern.
 */
export async function djangoFetch(path: string, init: RequestInit = {}): Promise<Response> {
  const store = await cookies();
  const cookieHeader = store
    .getAll()
    .map((cookie) => `${cookie.name}=${cookie.value}`)
    .join("; ");

  const headers = new Headers(init.headers);
  headers.set("Cookie", cookieHeader);
  if (init.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const method = (init.method ?? "GET").toUpperCase();
  if (!SAFE_METHODS.has(method)) {
    const csrftoken = store.get("csrftoken")?.value;
    if (csrftoken) {
      headers.set("X-CSRFToken", csrftoken);
    }
  }

  return fetch(`${DJANGO_API_URL}${path}`, { ...init, headers, cache: "no-store" });
}

/** djangoFetch, but parses the JSON body and throws DjangoApiError on non-2xx. */
export async function djangoJson<T = unknown>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await djangoFetch(path, init);
  const body = await response.json().catch(() => null);
  if (!response.ok) {
    throw new DjangoApiError(response.status, body);
  }
  return body as T;
}

/**
 * Relays every Set-Cookie header from a Django response onto the current
 * Next.js response's cookie jar. Only callable from a Server Action or Route
 * Handler (Next.js enforces this) — use right after login/logout calls.
 */
export async function relayCookies(response: Response): Promise<void> {
  const store = await cookies();
  const setCookieHeaders = response.headers.getSetCookie?.() ?? [];
  for (const raw of setCookieHeaders) {
    const parsed = parseSetCookie(raw);
    if (parsed) {
      store.set(parsed.name, parsed.value, parsed.options);
    }
  }
}

type ParsedCookie = {
  name: string;
  value: string;
  options: {
    path?: string;
    httpOnly?: boolean;
    secure?: boolean;
    sameSite?: "lax" | "strict" | "none";
    maxAge?: number;
    expires?: Date;
  };
};

function parseSetCookie(raw: string): ParsedCookie | null {
  const segments = raw.split(";").map((segment) => segment.trim());
  const [nameValue, ...attributeSegments] = segments;
  const eqIndex = nameValue.indexOf("=");
  if (eqIndex === -1) return null;

  const name = nameValue.slice(0, eqIndex);
  const value = nameValue.slice(eqIndex + 1);
  const options: ParsedCookie["options"] = {};

  for (const attribute of attributeSegments) {
    const [rawKey, rawValue] = attribute.split("=");
    switch (rawKey.trim().toLowerCase()) {
      case "path":
        options.path = rawValue;
        break;
      case "max-age":
        options.maxAge = Number(rawValue);
        break;
      case "expires":
        options.expires = new Date(rawValue);
        break;
      case "samesite":
        options.sameSite = rawValue?.toLowerCase() as "lax" | "strict" | "none" | undefined;
        break;
      case "httponly":
        options.httpOnly = true;
        break;
      case "secure":
        options.secure = true;
        break;
    }
  }

  return { name, value, options };
}
