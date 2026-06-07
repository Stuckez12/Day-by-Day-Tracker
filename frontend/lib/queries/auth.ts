"use client";

import { err, ok, Result } from "neverthrow";
import { validateEmail } from "@/lib/common/validation/validateEmail";
import { validatePassword } from "@/lib/common/validation/validatePassword";
import { ValidationErrorProp } from "@/lib/interfaces/common";
import { PersonnelLogin } from "@/lib/interfaces/personnel";

const base_url = process.env.NEXT_PUBLIC_API_URL;

export async function personnelLoginQuery(
  form: PersonnelLogin,
): Promise<Result<void, ValidationErrorProp>> {
  const email_errors = validateEmail(form.email);
  const password_errors = validatePassword(form.email);

  const validation_errors = [...email_errors, ...password_errors];

  if (validation_errors.length > 0) {
    return err({
      api_response: false,
      error_count: validation_errors.length,
      errors: { email: email_errors, password: password_errors },
    });
  }

  const response = await fetch(`${base_url}/api/v1/auth/login`, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(form),
  });
  if (response.ok) {
    return ok();
  }

  const detail_err = await response.json();
  return err({
    api_response: true,
    error_count: 1,
    errors: { api: detail_err.detail },
  });
}
