import { getBearerHeaders } from "@/lib/common/auth/getAccessToken";
import { validateEmail } from "@/lib/common/validation/validateEmail";
import { validatePassword } from "@/lib/common/validation/validatePassword";
import { Result, ValidationErrorProp } from "@/lib/interfaces/common";
import {
  PersonnelProp,
  UpdatePersonnelEmail,
  UpdatePersonnelInfo,
  UpdatePersonnelPassword,
} from "@/lib/interfaces/personnel";

const BASE_API_URL = process.env.NEXT_PUBLIC_BASE_API_URL;
const unauthorized = (): Result<never, ValidationErrorProp> => ({
  ok: false,
  error: {
    api_response: true,
    error_count: 1,
    errors: { api: ["Your session has expired. Please sign in again."] },
  },
});

async function personnelRequest<T>(
  path: string,
  init: RequestInit = {},
): Promise<Result<T, ValidationErrorProp>> {
  const authorization = await getBearerHeaders();
  if (!authorization) return unauthorized();

  const response = await fetch(`${BASE_API_URL}/api/v1/personal${path}`, {
    ...init,
    headers: {
      ...authorization,
      ...(init.body ? { "Content-Type": "application/json" } : {}),
    },
  });
  const body = await response.json();

  return response.ok
    ? { ok: true, data: body }
    : {
        ok: false,
        error: {
          api_response: true,
          error_count: 1,
          errors: { api: [body.detail ?? "Request failed"] },
        },
      };
}

export function getPersonnelQuery() {
  return personnelRequest<PersonnelProp>("/me");
}

export function updatePersonnelInfoQuery(form: UpdatePersonnelInfo) {
  return personnelRequest<PersonnelProp>("/me/details", {
    method: "PUT",
    body: JSON.stringify(form),
  });
}

export async function updatePersonnelEmailQuery(
  form: UpdatePersonnelEmail,
): Promise<Result<PersonnelProp, ValidationErrorProp>> {
  const errors = validateEmail(form.email);
  if (errors.length) {
    return {
      ok: false,
      error: { api_response: false, error_count: errors.length, errors: { api: errors } },
    };
  }

  return personnelRequest<PersonnelProp>("/me/email", {
    method: "PUT",
    body: JSON.stringify(form),
  });
}

export async function updatePersonnelPasswordQuery(
  form: UpdatePersonnelPassword,
): Promise<Result<PersonnelProp, ValidationErrorProp>> {
  const errors = validatePassword(form.new_password);
  if (errors.length) {
    return {
      ok: false,
      error: { api_response: false, error_count: errors.length, errors: { api: errors } },
    };
  }
  if (form.new_password !== form.confirm_password) {
    return {
      ok: false,
      error: { api_response: false, error_count: 1, errors: { new_password: ["Passwords do not match"] } },
    };
  }

  return personnelRequest<PersonnelProp>("/me/password", {
    method: "PUT",
    body: JSON.stringify(form),
  });
}
