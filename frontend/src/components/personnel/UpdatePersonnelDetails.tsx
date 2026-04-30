import { useState } from "react";

import type { PersonnelDetailsProps } from "interfaces/personnel";

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

  return (
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
  );
}

export default UpdatePersonnelDetails;
