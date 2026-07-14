"use server";

import { redirect } from "next/navigation";
import { cookies } from "next/headers";

import { djangoFetch, relayCookies } from "@/lib/django";

export type LoginState = { error?: string } | undefined;

export async function login(_prevState: LoginState, formData: FormData): Promise<LoginState> {
  const username = formData.get("username");
  const password = formData.get("password");

  if (typeof username !== "string" || typeof password !== "string" || !username || !password) {
    return { error: "Username and password are required." };
  }

  const response = await djangoFetch("/api/auth/login/", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
  await relayCookies(response);

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    return { error: body?.detail ?? "Login failed. Please try again." };
  }

  redirect("/dashboard");
}

export async function logout(): Promise<void> {
  const response = await djangoFetch("/api/auth/logout/", { method: "POST" });
  await relayCookies(response);

  const store = await cookies();
  store.delete("sessionid");
  store.delete("csrftoken");

  redirect("/login");
}
