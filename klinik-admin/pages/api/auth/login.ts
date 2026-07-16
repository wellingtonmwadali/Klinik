import type { NextApiRequest, NextApiResponse } from "next";

import { djangoFetch, relayCookies } from "@/lib/django";

type Body = { error?: string };

export default async function handler(req: NextApiRequest, res: NextApiResponse<Body>) {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).json({ error: "Method not allowed" });
  }

  const { username, password } = req.body ?? {};
  if (typeof username !== "string" || typeof password !== "string" || !username || !password) {
    return res.status(400).json({ error: "Username and password are required." });
  }

  const djangoResponse = await djangoFetch(req, "/api/auth/login/", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
  relayCookies(res, djangoResponse);

  if (!djangoResponse.ok) {
    const body = await djangoResponse.json().catch(() => null);
    return res.status(djangoResponse.status).json({ error: body?.detail ?? "Login failed. Please try again." });
  }

  return res.status(200).json({});
}
