import { useState } from "react";

import ListErrors from "@/components/common/errors/ListErrors";
import PasswordInput from "@/components/common/form-inputs/PasswordInput";
import SubmitButton from "@/components/common/form-inputs/SubmitButton";
import TextInput from "@/components/common/form-inputs/TextInput";
import { updateForm } from "@/lib/common/updateForm";
import { PersonnelLogin } from "@/lib/interfaces/personnel";
import { personnelLoginQuery } from "@/lib/queries/auth";

export default function LoginForm() {
  const [errors, setErrors] = useState<Record<string, string[]>>({});
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

    setErrors(queryError.error.errors);

    console.log("Errors:", queryError);
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
        <ListErrors errors={errors.email}></ListErrors>
        <ListErrors errors={errors.password}></ListErrors>
        <SubmitButton label="Submit" onSubmit={submitForm} />
      </form>
    </div>
  );
}
