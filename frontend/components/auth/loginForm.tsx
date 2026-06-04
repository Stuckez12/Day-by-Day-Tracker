import { useState } from "react";

import PasswordInput from "@/components/common/form-inputs/PasswordInput";
import SubmitButton from "@/components/common/form-inputs/SubmitButton";
import TextInput from "@/components/common/form-inputs/TextInput";
import { updateForm } from "@/lib/common/updateForm";
import { PersonnelLogin } from "@/lib/interfaces/personnel";
import { personnelLoginQuery } from "@/lib/queries/auth";

export default function LoginForm() {
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

    const [error, _] = await personnelLoginQuery(form);

    console.log("Errors:", error);
  }

  return (
    <div>
      <form>
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
        <SubmitButton label="Submit" onSubmit={submitForm} />
      </form>
    </div>
  );
}
