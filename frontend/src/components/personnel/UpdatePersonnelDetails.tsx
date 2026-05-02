import { useState } from "react";

import type {
  PersonnelDetailsProps,
  PersonnelProps,
} from "interfaces/personnel";

import APICall from "scripts/api.ts";

import "styles/auth/login-form.scss";
import "styles/pages/personnel.scss";

function UpdatePersonnelDetails() {
  const [form, setForm] = useState<PersonnelDetailsProps>({
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

    async function update_email(form: PersonnelDetailsProps) {
      const [success, data, message] = await APICall.put<PersonnelProps>(
        "/personal/me/details",
        {
          first_name: form.first_name,
          last_name: form.last_name,
        },
      );

      if (success) {
        console.log("Success. Now refresh");
        setForm(data!);
      } else {
        console.log("Error when getting data");
        console.log(message);
      }
    }

    update_email(form);
  }

  return (
    <>
      <div className="details-block">
        <div className="details-50">
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
        </div>

        <div className="details-50">
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
        </div>
      </div>
      <button className="submit-button" onClick={onSubmit}>
        Submit
      </button>
    </>
  );
}

export default UpdatePersonnelDetails;
