"use client";

import { useState } from "react";

import ListErrors from "@/components/common/errors/ListErrors";
import PasswordInput from "@/components/common/form-inputs/PasswordInput";
import { updateForm } from "@/lib/common/updateForm";
import { UpdatePersonnelPassword } from "@/lib/interfaces/personnel";
import { updatePersonnelPasswordQuery } from "@/lib/queries/personnel";
import SubmitButton from "@/components/common/form-inputs/SubmitButton";

export default function UpdatePasswordForm() {
  const [errors, setErrors] = useState<string[]>([]);
  const [form, setForm] = useState<UpdatePersonnelPassword>({
    current_password: "",
    new_password: "",
    confirm_password: "",
  });

  function onChange(e: React.ChangeEvent<HTMLInputElement>) {
    return updateForm(e, form, setForm);
  }

  async function submitForm(e: React.SubmitEvent<HTMLFormElement>) {
    e.preventDefault();

    console.log("Form data:", form);

    const result = await updatePersonnelPasswordQuery(form);

    if (result.ok) {
      console.log("Password Updated Successfully");

      setErrors([]);

      return;
    }

    const all_errors = result.error.errors;
    let display_errors: string[] = [];

    if (result.error.api_response) {
      display_errors = [`${all_errors.api}`];
    } else {
      display_errors = display_errors.concat(all_errors.new_password);
    }

    setErrors(display_errors);
  }

  return (
    <div>
      <form onSubmit={submitForm}>
        <h1>Update Password</h1>
        <PasswordInput
          name="current_password"
          label="Current Password"
          value={form.current_password}
          onChange={onChange}
        />
        <PasswordInput
          name="new_password"
          label="New Password"
          value={form.new_password}
          onChange={onChange}
        />
        <PasswordInput
          name="confirm_password"
          label="Confirm Password"
          value={form.confirm_password}
          onChange={onChange}
        />
        <ListErrors errors={errors} />
        <SubmitButton label="Submit" />
      </form>
    </div>
  );
}
