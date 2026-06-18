"use client";

import { useContext, useEffect, useState } from "react";

import { PartialPersonnelContext } from "@/components/common/contexts/personnelContext";
import ListErrors from "@/components/common/errors/ListErrors";
import SubmitButton from "@/components/common/form-inputs/SubmitButton";
import TextInput from "@/components/common/form-inputs/TextInput";
import { updateForm } from "@/lib/common/updateForm";
import { UpdatePersonnelInfo } from "@/lib/interfaces/personnel";
import { updatePersonnelInfoQuery } from "@/lib/queries/personnel";

export default function UpdateInfoForm() {
  const [errors, setErrors] = useState<string[]>([]);
  const { partialPersonnel } = useContext(PartialPersonnelContext);
  const [form, setForm] = useState<UpdatePersonnelInfo>({
    first_name: "",
    last_name: "",
  });

  useEffect(() => {
    if (partialPersonnel.id != undefined) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setForm(partialPersonnel as UpdatePersonnelInfo);
    }
  }, [partialPersonnel]);

  function onChange(e: React.ChangeEvent<HTMLInputElement>) {
    return updateForm(e, form, setForm);
  }

  async function submitForm(e: React.MouseEvent<HTMLButtonElement>) {
    e.preventDefault();

    console.log("Form data:", form);

    const result = await updatePersonnelInfoQuery(form);

    if (result.isOk()) {
      console.log("Info Updated Successfully");

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
  }

  return (
    <div>
      <form>
        <h1>Update Info</h1>
        <TextInput
          name="first_name"
          label="First Name"
          value={form.first_name}
          onChange={onChange}
        />
        <TextInput
          name="last_name"
          label="Last Name"
          value={form.last_name}
          onChange={onChange}
        />
        <ListErrors errors={errors} />
        <SubmitButton label="Submit" onSubmit={submitForm} />
      </form>
    </div>
  );
}
