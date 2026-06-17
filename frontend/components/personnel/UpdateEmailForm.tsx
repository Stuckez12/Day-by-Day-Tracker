"use client";

import { useContext, useEffect, useState } from "react";

import { PartialPersonnelContext } from "@/components/common/contexts/personnelContext";
import ListErrors from "@/components/common/errors/ListErrors";
import TextInputWButton from "@/components/common/form-inputs/TextInputWButton";
import { updateForm } from "@/lib/common/updateForm";
import { UpdatePersonnelEmail } from "@/lib/interfaces/personnel";
import { updatePersonnelEmailQuery } from "@/lib/queries/personnel";

export default function UpdateEmailForm() {
  const [errors, setErrors] = useState<string[]>([]);
  const { partialPersonnel } = useContext(PartialPersonnelContext);
  const [form, setForm] = useState<UpdatePersonnelEmail>({
    email: "",
  });

  useEffect(() => {
    if (partialPersonnel.id != undefined) {
      setForm(partialPersonnel as UpdatePersonnelEmail);
    }
  }, [partialPersonnel]);

  function onChange(e: React.ChangeEvent<HTMLInputElement>) {
    return updateForm(e, form, setForm);
  }

  async function submitForm(e: React.MouseEvent<HTMLButtonElement>) {
    e.preventDefault();

    console.log("Form data:", form);

    const result = await updatePersonnelEmailQuery(form);

    if (result.isOk()) {
      console.log("Email Updated Successfully");

      setErrors([]);
      setForm(result.value);

      return;
    }

    const all_errors = result.error.errors;
    let display_errors: string[] = [];

    if (result.error.api_response) {
      display_errors = [`${all_errors.api}`];
    } else {
      display_errors = display_errors.concat(all_errors.email);
    }

    setErrors(display_errors);

    console.log("All errors:", all_errors);
    console.log("Errors:", display_errors);
  }

  return (
    <div>
      <form>
        <h1>Update Email</h1>
        <TextInputWButton
          name="email"
          type="email"
          label="Email"
          value={form.email}
          onChange={onChange}
          button_label="Update"
          onSubmit={submitForm}
        />
        <ListErrors errors={errors}></ListErrors>
      </form>
    </div>
  );
}
