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
  const { id } = req.query;

  if (req.method === "GET") {
    const djangoResponse = await djangoFetch(req, `/api/doctors/${id}/work-schedule/`, { method: "GET" });
    const text = await djangoResponse.text();
    const contentType = djangoResponse.headers.get("content-type");
    if (contentType) res.setHeader("Content-Type", contentType);
    return res.status(djangoResponse.status).send(text);
  }

  if (req.method === "PUT") {
    const body = await readRawBody(req);
    const djangoResponse = await djangoFetch(req, `/api/doctors/${id}/work-schedule/`, {
      method: "PUT",
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
    return res.status(djangoResponse.status).send(text);
  }

  res.setHeader("Allow", "GET, PUT");
  return res.status(405).end();
}
