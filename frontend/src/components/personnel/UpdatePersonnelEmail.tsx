import { useState } from "react";

import type { PersonnelEmailProps } from "interfaces/personnel";

import "styles/auth/login-form.scss";

function UpdatePersonnelEmail() {
  const [form, setForm] = useState<PersonnelEmailProps>({
    email: "",
  });

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const { name, value } = e.target;
    setForm({
      ...form,
      [name]: value,
    });
  }

  return (
    <div className="details-block-single">
      <div className="text-input">
        <input
          type="text"
          name="email"
          value={form.email}
          onChange={handleChange}
          placeholder=""
          autoComplete="new-field"
        />
        <label>Email</label>
      </div>
    </div>
  );
}

export default UpdatePersonnelEmail;
