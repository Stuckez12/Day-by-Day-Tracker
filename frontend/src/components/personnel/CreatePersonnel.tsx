import React, { useContext, useState } from "react";

import { ContextRefreshPersonnelList } from "contexts/ContextRefreshPersonnelList.tsx";

import type {
  CreatePersonnelProps,
  PersonnelRowProps,
} from "interfaces/personnel";

import APICall from "scripts/api.ts";

import "styles/common/form-inputs.scss";

function CreatePersonnel() {
  const [form, setForm] = useState<CreatePersonnelProps>({
    first_name: "",
    last_name: "",
  });

  const { setRefreshList } = useContext(ContextRefreshPersonnelList);

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
        },
      );

      if (success) {
        console.log("Success. Now refresh");
        setRefreshList(true);
      } else {
        console.log("Error when getting data");
        console.log(message);
      }
    }

    create_personnel(form);
  }

  return (
    <form>
      <h1 className="form-title">Create New Personnel</h1>
      <div className="text-input">
        <input
          type="text"
          name="first_name"
          value={form.first_name}
          onChange={handleChange}
          placeholder=""
          autoComplete="new-field"
        />
        <label>First Name</label>
      </div>

      <div className="text-input">
        <input
          type="text"
          name="last_name"
          value={form.last_name}
          onChange={handleChange}
          placeholder=""
          autoComplete="new-field"
        />
        <label>Last Name</label>
      </div>
      <button className="submit-button" onClick={onSubmit}>
        Submit
      </button>
    </form>
  );
}

export default CreatePersonnel;
