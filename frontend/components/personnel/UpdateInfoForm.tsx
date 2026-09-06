"use client";

import { useContext, useEffect, useState } from "react";

import { PartialPersonnelContext } from "@/components/common/contexts/personnelContext";
import ListErrors from "@/components/common/errors/ListErrors";
import Button from "@/components/common/buttons/Button";
import TextInput from "@/components/common/form-inputs/TextInput";
import { updateForm } from "@/lib/common/updateForm";
import { UpdatePersonnelInfo } from "@/lib/interfaces/personnel";
import { updatePersonnelInfoQuery } from "@/lib/queries/personnel";

export default function UpdateInfoForm() {
  const [errors, setErrors] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
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

  async function submitForm(e: React.SubmitEvent<HTMLFormElement>) {
    e.preventDefault();

    console.log("Form data:", form);
    setIsLoading(true);

    const result = await updatePersonnelInfoQuery(form);

    if (result.ok) {
      console.log("Info Updated Successfully");

      setErrors([]);
      setForm(result.data);
      setIsLoading(false);

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
    setIsLoading(false);
  }

  return (
    <div>
      <form onSubmit={submitForm}>
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
        <Button loading={isLoading}>Submit</Button>
      </form>
    </div>
  );
}
