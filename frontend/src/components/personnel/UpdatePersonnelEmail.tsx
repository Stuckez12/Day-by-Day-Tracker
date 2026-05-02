import { useContext, useEffect, useState } from "react";

import { ContextPersonnelForms } from "contexts/ContextPersonnelForms";

import type { PersonnelEmailProps, PersonnelProps } from "interfaces/personnel";

import APICall from "scripts/api.ts";

import "styles/auth/login-form.scss";

function UpdatePersonnelEmail() {
  const { refreshPersonnelForms } = useContext(ContextPersonnelForms);

  const [form, setForm] = useState<PersonnelEmailProps>(refreshPersonnelForms);

  useEffect(() => {
    setForm(refreshPersonnelForms);
  }, [refreshPersonnelForms]);

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

    async function update_email(form: PersonnelEmailProps) {
      const [success, data, message] = await APICall.put<PersonnelProps>(
        "/personal/me/email",
        {
          email: form.email,
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
    <div>
      <h1>Update Email</h1>
      <div className="details-block-single">
        <div className="text-input-button">
          <input
            type="text"
            name="email"
            value={form.email}
            onChange={handleChange}
            placeholder=""
            autoComplete="new-field"
          />
          <label>Email</label>
          <button onClick={onSubmit}>Submit</button>
        </div>
      </div>
    </div>
  );
}

export default UpdatePersonnelEmail;
