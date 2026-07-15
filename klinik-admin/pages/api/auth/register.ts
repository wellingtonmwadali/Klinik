import type { NextApiRequest, NextApiResponse } from "next";

import { djangoFetch } from "@/lib/django";

type Body = {
  error?: string;
  message?: string;
};

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<Body>
) {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).json({ error: "Method not allowed" });
  }

  const djangoResponse = await djangoFetch(
    req,
    "/api/patients/register/",
    {
      method: "POST",
      body: JSON.stringify(req.body),
    }
  );

  const body = await djangoResponse.json().catch(() => null);

  return res.status(djangoResponse.status).json(
    body ?? {
      message: "Patient registered successfully.",
    }
  );
}