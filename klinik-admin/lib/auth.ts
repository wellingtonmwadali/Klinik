import type { IncomingMessage } from "http";

import { DjangoApiError, djangoJson } from "@/lib/django";

export type Me = {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: string | null;
  is_staff: boolean;
};

/** Fetches the current user; returns null (does not throw) if unauthenticated. */
export async function fetchMe(req: Pick<IncomingMessage, "headers">): Promise<Me | null> {
  try {
    return await djangoJson<Me>(req, "/api/auth/me/");
  } catch (error) {
    if (error instanceof DjangoApiError && (error.status === 401 || error.status === 403)) {
      return null;
    }
    throw error;
  }
}
