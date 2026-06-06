"use server";

import { err, ok, Result } from "neverthrow";
import { cookies } from "next/headers";

import { ValidationErrorProp } from "@/lib/interfaces/common";
import { PersonnelProp } from "@/lib/interfaces/personnel";

const base_url = process.env.NEXT_PUBLIC_API_URL;

export async function getPersonnelQuery(): Promise<
  Result<PersonnelProp, ValidationErrorProp>
> {
  const cookieStore = await cookies();
  const token = cookieStore.get("personnel_id")?.value;

  console.log(`${base_url}/api/v1/personal/me`);

  const response = await fetch(`${base_url}/api/v1/personal/me`, {
    method: "GET",
    headers: {
      Cookie: `personnel_id=${token}`,
    },
  });
  const body = await response.json();

  if (response.ok) {
    return ok(body);
  }

  return err({
    api_response: true,
    error_count: 1,
    errors: { api: body.detail },
  });
}
