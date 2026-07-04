"use client";

import { validateEmail } from "@/lib/common/validation/validateEmail";
import { validatePassword } from "@/lib/common/validation/validatePassword";
import { Result, ValidationErrorProp } from "@/lib/interfaces/common";
import { PersonnelLogin } from "@/lib/interfaces/personnel";
import { BASE_API_URL } from "../common/envParams";

export async function personnelLoginQuery(
  form: PersonnelLogin,
): Promise<Result<null, ValidationErrorProp>> {
  const email_errors = validateEmail(form.email);
  const password_errors = validatePassword(form.email);

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
    return { ok: true, data: null };
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

export async function personnelLogoutQuery(): Promise<
  Result<void, ValidationErrorProp>
> {
  const response = await fetch(`${BASE_API_URL}/api/v1/auth/logout`, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
  });
  const body = await response.json();

  if (response.ok) {
    return { ok: true, data: body };
  }

  return {
    ok: false,
    error: {
      api_response: true,
      error_count: 1,
      errors: { api: body.detail },
    },
  };
}
