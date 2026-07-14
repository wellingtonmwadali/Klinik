import { redirect } from "next/navigation";

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

/** Fetches the current user, redirecting to /login if the session is missing/expired. */
export async function requireMe(): Promise<Me> {
  try {
    return await djangoJson<Me>("/api/auth/me/");
  } catch (error) {
    if (error instanceof DjangoApiError && (error.status === 401 || error.status === 403)) {
      redirect("/login");
    }
    throw error;
  }
}
