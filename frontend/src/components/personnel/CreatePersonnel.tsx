import React, { useState } from "react";

import type {
  CreatePersonnelProps,
  PersonnelRowProps,
} from "interfaces/personnel";

import APICall from "scripts/api.ts";

function CreatePersonnel() {
  const [form, setForm] = useState<CreatePersonnelProps>({
    first_name: "",
    last_name: "",
  });

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const { name, value } = e.target;
    setForm({
      ...form,
      [name]: value,
    });
  }

  function onSubmit(e: React.MouseEvent<HTMLButtonElement>) {
    e.preventDefault();

    console.log("Form data:", form);

    async function create_personnel(form: CreatePersonnelProps) {
      const [success, _, message] = await APICall.post<PersonnelRowProps>(
        "/personal",
        {
          first_name: form.first_name,
          last_name: form.last_name,
        }
      );

      if (success) {
        console.log("Success. Now refresh");
      } else {
        console.log("Error when getting data");
        console.log(message);
      }
    }

    create_personnel(form);
  }

  return (
    <form>
      <label>
        Enter your name:
        <input
          type="text"
          name="first_name"
          value={form.first_name}
          onChange={handleChange}
        />
      </label>
      <label>
        Enter your last name:
        <input
          type="text"
          name="last_name"
          value={form.last_name}
          onChange={handleChange}
        />
      </label>
      <p>
        Current data: {form.first_name} | {form.last_name}
      </p>
      <button onClick={onSubmit}>Submit</button>
    </form>
  );
}

export default CreatePersonnel;
