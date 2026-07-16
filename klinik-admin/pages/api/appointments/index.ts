import type { NextApiRequest, NextApiResponse } from "next";

import { djangoFetch, relayCookies } from "@/lib/django";

export const config = { api: { bodyParser: false } };

async function readRawBody(req: NextApiRequest): Promise<string> {
  const chunks: Buffer[] = [];
  for await (const chunk of req) {
    chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk));
  }
  return Buffer.concat(chunks).toString("utf8");
}

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).end();
  }

  const body = await readRawBody(req);

  const djangoResponse = await djangoFetch(req, "/api/appointments/", {
    method: "POST",
    body,
    headers: { "Content-Type": "application/json" },
  });

  try {
    relayCookies(res, djangoResponse);
  } catch (e) {
    console.error("relayCookies failed:", e);
  }

  const text = await djangoResponse.text();
  const contentType = djangoResponse.headers.get("content-type");
  if (contentType) res.setHeader("Content-Type", contentType);
  res.status(djangoResponse.status).send(text);
}
