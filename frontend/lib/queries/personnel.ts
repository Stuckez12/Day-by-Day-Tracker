"use client";

import Cookies from "js-cookie";
import { Result, ValidationErrorProp } from "@/lib/interfaces/common";
import {
  PersonnelProp,
  UpdatePersonnelEmail,
  UpdatePersonnelInfo,
  UpdatePersonnelPassword,
} from "@/lib/interfaces/personnel";
import { validateEmail } from "@/lib/common/validation/validateEmail";
import { validatePassword } from "@/lib/common/validation/validatePassword";
import { BASE_API_URL } from "../common/envParams";

export async function getPersonnelQuery(): Promise<
  Result<PersonnelProp, ValidationErrorProp>
> {
  const token = Cookies.get("personnel_id");
  const response = await fetch(`${BASE_API_URL}/api/v1/personal/me`, {
    method: "GET",
    headers: {
      Cookie: `personnel_id=${token}`,
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

export async function updatePersonnelInfoQuery(
  form: UpdatePersonnelInfo,
): Promise<Result<PersonnelProp, ValidationErrorProp>> {
  const token = Cookies.get("personnel_id");
  const response = await fetch(`${BASE_API_URL}/api/v1/personal/me/details`, {
    method: "PUT",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      Cookie: `personnel_id=${token}`,
    },
    body: JSON.stringify(form),
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

export async function updatePersonnelEmailQuery(
  form: UpdatePersonnelEmail,
): Promise<Result<PersonnelProp, ValidationErrorProp>> {
  const email_errors = validateEmail(form.email);

  if (email_errors.length > 0) {
    return {
      ok: false,
      error: {
        api_response: false,
        error_count: email_errors.length,
        errors: { api: email_errors },
      },
    };
  }

  const token = Cookies.get("personnel_id");
  const response = await fetch(`${BASE_API_URL}/api/v1/personal/me/email`, {
    method: "PUT",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      Cookie: `personnel_id=${token}`,
    },
    body: JSON.stringify(form),
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

export async function updatePersonnelPasswordQuery(
  form: UpdatePersonnelPassword,
): Promise<Result<PersonnelProp, ValidationErrorProp>> {
  const password_errors = validatePassword(form.new_password);

  if (password_errors.length > 0) {
    return {
      ok: false,
      error: {
        api_response: false,
        error_count: password_errors.length,
        errors: { api: password_errors },
      },
    };
  }

  if (form.new_password != form.confirm_password) {
    return {
      ok: false,
      error: {
        api_response: false,
        error_count: 1,
        errors: { new_password: ["Passwords do not match"] },
      },
    };
  }

  const token = Cookies.get("personnel_id");
  const response = await fetch(`${BASE_API_URL}/api/v1/personal/me/password`, {
    method: "PUT",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      Cookie: `personnel_id=${token}`,
    },
    body: JSON.stringify(form),
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
