"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import ListErrors from "@/components/common/errors/ListErrors";
import PasswordInput from "@/components/common/form-inputs/PasswordInput";
import SubmitButton from "@/components/common/form-inputs/SubmitButton";
import TextInput from "@/components/common/form-inputs/TextInput";
import { updateForm } from "@/lib/common/updateForm";
import { PersonnelLogin } from "@/lib/interfaces/personnel";
import { personnelLoginQuery } from "@/lib/queries/auth";

import "@/styles/forms/login-form.scss";

export default function LoginForm() {
  const router = useRouter();

  const [errors, setErrors] = useState<string[]>([]);
  const [form, setForm] = useState<PersonnelLogin>({
    email: "",
    password: "",
  });

  function onChange(e: React.ChangeEvent<HTMLInputElement>) {
    return updateForm(e, form, setForm);
  }

  async function submitForm(e: React.MouseEvent<HTMLButtonElement>) {
    e.preventDefault();

    console.log("Form data:", form);

    const [queryError, _] = await personnelLoginQuery(form);

    if (queryError == null) {
      console.log("Login Success. Routing to homepage");
      router.push("/tracker");
      return;
    }

    const all_errors = queryError.error.errors;
    let display_errors: string[] = [];

    if (queryError.error.api_response) {
      display_errors = [`${all_errors.api}`];
    } else {
      display_errors = display_errors.concat(all_errors.email);
      display_errors = display_errors.concat(all_errors.password);
    }

    setErrors(display_errors);
  }

  return (
    <div className="login-form-container">
      <form className="login-form">
        <h1>Login</h1>
        <TextInput
          name="email"
          type="email"
          label="Email"
          value={form.email}
          onChange={onChange}
        />
        <PasswordInput
          name="password"
          label="Password"
          value={form.password}
          onChange={onChange}
        />
        <ListErrors errors={errors} />
        <SubmitButton label="Submit" onSubmit={submitForm} />
      </form>
    </div>
  );
}
