"use client";

import Cookies from "js-cookie";
import { err, ok, Result } from "neverthrow";

import { ValidationErrorProp } from "@/lib/interfaces/common";
import {
  PersonnelProp,
  UpdatePersonnelEmail,
  UpdatePersonnelInfo,
  UpdatePersonnelPassword,
} from "@/lib/interfaces/personnel";
import { validateEmail } from "@/lib/common/validation/validateEmail";
import { validatePassword } from "@/lib/common/validation/validatePassword";

const base_url = process.env.NEXT_PUBLIC_API_URL;

export async function getPersonnelQuery(): Promise<
  Result<PersonnelProp, ValidationErrorProp>
> {
  const token = Cookies.get("personnel_id");
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

export async function updatePersonnelInfoQuery(
  form: UpdatePersonnelInfo,
): Promise<Result<PersonnelProp, ValidationErrorProp>> {
  const response = await fetch(`${base_url}/api/v1/personal/me/details`, {
    method: "PUT",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(form),
  });

  const details = await response.json();
  if (response.ok) {
    return ok(details);
  }

  return err({
    api_response: true,
    error_count: 1,
    errors: { api: details.detail },
  });
}

export async function updatePersonnelEmailQuery(
  form: UpdatePersonnelEmail,
): Promise<Result<PersonnelProp, ValidationErrorProp>> {
  const email_errors = validateEmail(form.email);

  if (email_errors.length > 0) {
    return err({
      api_response: false,
      error_count: email_errors.length,
      errors: { email: email_errors },
    });
  }

  const response = await fetch(`${base_url}/api/v1/personal/me/email`, {
    method: "PUT",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(form),
  });

  const details = await response.json();
  if (response.ok) {
    return ok(details);
  }

  return err({
    api_response: true,
    error_count: 1,
    errors: { api: details.detail },
  });
}

export async function updatePersonnelPasswordQuery(
  form: UpdatePersonnelPassword,
): Promise<Result<PersonnelProp, ValidationErrorProp>> {
  const password_errors = validatePassword(form.new_password);

  if (password_errors.length > 0) {
    return err({
      api_response: false,
      error_count: password_errors.length,
      errors: { new_password: password_errors },
    });
  }

  if (form.new_password != form.confirm_password) {
    return err({
      api_response: false,
      error_count: 1,
      errors: { new_password: ["Passwords do not match"] },
    });
  }

  const response = await fetch(`${base_url}/api/v1/personal/me/password`, {
    method: "PUT",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(form),
  });

  const details = await response.json();
  if (response.ok) {
    return ok(details);
  }

  return err({
    api_response: true,
    error_count: 1,
    errors: { api: details.detail },
  });
}
