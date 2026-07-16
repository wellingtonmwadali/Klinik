import type { NextApiRequest, NextApiResponse } from "next";

import { appendSetCookie, djangoFetch, relayCookies } from "@/lib/django";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).end();
  }

  const djangoResponse = await djangoFetch(req, "/api/auth/logout/", { method: "POST" });
  relayCookies(res, djangoResponse);

  appendSetCookie(res, "sessionid=; Path=/; Max-Age=0");
  appendSetCookie(res, "csrftoken=; Path=/; Max-Age=0");

  res.redirect(303, "/");
}
