import { getAccessToken } from "@/lib/common/auth/getAccessToken";
import { validateEmail } from "@/lib/common/validation/validateEmail";
import { validatePassword } from "@/lib/common/validation/validatePassword";
import { Result, ValidationErrorProp } from "@/lib/interfaces/common";
import {
  PersonnelProp,
  UpdatePersonnelEmail,
  UpdatePersonnelInfo,
  UpdatePersonnelPassword,
} from "@/lib/interfaces/personnel";
import { APICall, MustBeLoggedIn } from "@/lib/queries/base";

const API = new APICall(process.env.NEXT_PUBLIC_BASE_API_URL!);

export async function getPersonnelQuery() {
  const token = await getAccessToken();
  if (!token) {
    return MustBeLoggedIn;
  }

  return await API.get<PersonnelProp>({
    url_path: "/v1/personal/me",
    token: token,
  });
}

export async function updatePersonnelInfoQuery(form: UpdatePersonnelInfo) {
  const token = await getAccessToken();
  if (!token) {
    return MustBeLoggedIn;
  }

  return await API.put<PersonnelProp>({
    url_path: "/v1/personal/me/details",
    token: token,
    body: form,
  });
}

export async function updatePersonnelEmailQuery(
  form: UpdatePersonnelEmail,
): Promise<Result<PersonnelProp, ValidationErrorProp>> {
  const token = await getAccessToken();
  if (!token) {
    return MustBeLoggedIn;
  }

  const errors = validateEmail(form.email);
  if (errors.length) {
    return {
      ok: false,
      error: {
        api_response: false,
        error_count: errors.length,
        errors: { api: errors },
      },
    };
  }

  return await API.put<PersonnelProp>({
    url_path: "/v1/personal/me/email",
    token: token,
    body: form,
  });
}

export async function updatePersonnelPasswordQuery(
  form: UpdatePersonnelPassword,
): Promise<Result<PersonnelProp, ValidationErrorProp>> {
  const token = await getAccessToken();
  if (!token) {
    return MustBeLoggedIn;
  }

  const errors = validatePassword(form.new_password);
  if (errors.length) {
    return {
      ok: false,
      error: {
        api_response: false,
        error_count: errors.length,
        errors: { api: errors },
      },
    };
  }
  if (form.new_password !== form.confirm_password) {
    return {
      ok: false,
      error: {
        api_response: false,
        error_count: 1,
        errors: { new_password: ["Passwords do not match"] },
      },
    };
  }

  return await API.put<PersonnelProp>({
    url_path: "/v1/personal/me/password",
    token: token,
    body: form,
  });
}
