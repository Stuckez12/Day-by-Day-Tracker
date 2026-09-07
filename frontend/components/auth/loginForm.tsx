"use client";

import { useRouter } from "next/navigation";
import { signIn } from "next-auth/react";
import { useState } from "react";

import ListErrors from "@/components/common/errors/ListErrors";
import PasswordInput from "@/components/common/form-inputs/PasswordInput";
import TextInput from "@/components/common/form-inputs/TextInput";
import { updateForm } from "@/lib/common/updateForm";
import { PersonnelLogin } from "@/lib/interfaces/personnel";
import Button from "../common/buttons/Button";

export default function LoginForm() {
  const router = useRouter();

  const [errors, setErrors] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [form, setForm] = useState<PersonnelLogin>({
    email: "",
    password: "",
  });

  function onChange(e: React.ChangeEvent<HTMLInputElement>) {
    return updateForm(e, form, setForm);
  }

  async function submitForm(e: React.SubmitEvent<HTMLFormElement>) {
    e.preventDefault();

    setIsLoading(true);

    const result = await signIn("credentials", {
      ...form,
      redirect: false,
    });

    if (result?.ok) {
      router.replace("/tracker");
      return;
    }

    setErrors(["Invalid email or password"]);
    setIsLoading(false);
  }

  return (
    <div className="mx-auto min-h-[calc(100vh-64px)] w-full">
      <form
        className="mx-auto mt-32 max-w-md p-8 max-sm:mt-16 max-sm:p-3"
        method="post"
        onSubmit={submitForm}
      >
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
        <Button loading={isLoading}>Submit</Button>
      </form>
    </div>
  );
}
