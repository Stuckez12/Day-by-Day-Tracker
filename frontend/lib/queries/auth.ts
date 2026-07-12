"use server";

import { getAccessToken } from "@/lib/common/auth/getAccessToken";
import { validateEmail } from "@/lib/common/validation/validateEmail";
import { validatePassword } from "@/lib/common/validation/validatePassword";
import { Result, ValidationErrorProp } from "@/lib/interfaces/common";
import { PersonnelLogin } from "@/lib/interfaces/personnel";
import { APICall, MustBeLoggedIn } from "@/lib/queries/base";

const API = new APICall(process.env.NEXT_PUBLIC_BASE_API_URL!);

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

  return await API.post<LoginResponse>({
    url_path: "/v1/auth/login",
    body: form,
  });
}
