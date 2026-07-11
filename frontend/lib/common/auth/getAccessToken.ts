"use client";

import { getSession } from "next-auth/react";

/** Returns the backend token that NextAuth stored for the active user. */
export async function getAccessToken(): Promise<string | null> {
  const session = await getSession();

  return session?.accessToken ?? null;
}

export async function getBearerHeaders(): Promise<HeadersInit | null> {
  const accessToken = await getAccessToken();

  return accessToken ? { Authorization: `Bearer ${accessToken}` } : null;
}
