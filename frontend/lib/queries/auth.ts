"use server";

import { validateEmail } from "@/lib/common/validation/validateEmail";
import { validatePassword } from "@/lib/common/validation/validatePassword";
import { Result, ValidationErrorProp } from "@/lib/interfaces/common";
import { PersonnelLogin } from "@/lib/interfaces/personnel";

// NextAuth runs on the server. In Docker it must reach the API over the
// service network rather than via the browser-facing URL.
const BASE_API_URL =
  process.env.API_INTERNAL_URL ?? process.env.NEXT_PUBLIC_BASE_API_URL;

export async function personnelLoginQuery(
  form: PersonnelLogin,
): Promise<Result<LoginResponse, ValidationErrorProp>> {
  const email_errors = validateEmail(form.email);
  const password_errors = validatePassword(form.password);

  const validation_errors = [...email_errors, ...password_errors];

  if (validation_errors.length > 0) {
    return {
      ok: false,
      error: {
        api_response: false,
        error_count: validation_errors.length,
        errors: { email: email_errors, password: password_errors },
      },
    };
  }

  const response = await fetch(`${BASE_API_URL}/api/v1/auth/login`, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(form),
  });

  if (response.ok) {
    return { ok: true, data: await response.json() };
  }

  const err = await response.json();

  return {
    ok: false,
    error: {
      api_response: true,
      error_count: 1,
      errors: { api: err.detail },
    },
  };
}

interface LoginResponse {
  access_token: string;
  token_type: "bearer";
  personnel: {
    id: string;
    email: string;
    first_name: string;
    last_name: string;
  };
}
