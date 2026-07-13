"use server";

import { getSession } from "next-auth/react";

export async function getAccessToken(): Promise<string | null> {
  const session = await getSession();

  return session?.accessToken ?? null;
}
