import type { NextApiRequest, NextApiResponse } from "next";

import { djangoFetch } from "@/lib/django";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== "GET") {
    res.setHeader("Allow", "GET");
    return res.status(405).end();
  }

  const search = req.url?.includes("?") ? req.url.slice(req.url.indexOf("?")) : "";
  const djangoResponse = await djangoFetch(req, `/api/patients/${search}`, { method: "GET" });

  const text = await djangoResponse.text();
  const contentType = djangoResponse.headers.get("content-type");
  if (contentType) res.setHeader("Content-Type", contentType);
  res.status(djangoResponse.status).send(text);
}
