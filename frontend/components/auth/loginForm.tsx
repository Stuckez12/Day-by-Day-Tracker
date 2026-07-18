"use client";

import { useRouter } from "next/navigation";
import { signIn } from "next-auth/react";
import { useState } from "react";

import ListErrors from "@/components/common/errors/ListErrors";
import PasswordInput from "@/components/common/form-inputs/PasswordInput";
import SubmitButton from "@/components/common/form-inputs/SubmitButton";
import TextInput from "@/components/common/form-inputs/TextInput";
import { updateForm } from "@/lib/common/updateForm";
import { PersonnelLogin } from "@/lib/interfaces/personnel";
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

  async function submitForm(e: React.SubmitEvent<HTMLFormElement>) {
    e.preventDefault();

    const result = await signIn("credentials", {
      ...form,
      redirect: false,
    });

    if (result?.ok) {
      router.replace("/tracker");
      return;
    }

    setErrors(["Invalid email or password"]);
  }

  return (
    <div className="login-form-container">
      <form className="login-form" method="post" onSubmit={submitForm}>
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
        <SubmitButton label="Submit" />
      </form>
    </div>
  );
}
