import { useState } from "react";

import type { PersonnelPasswordUpdateProps } from "interfaces/personnel";

import "styles/auth/login-form.scss";

function UpdatePersonnelPassword() {
  const [form, setForm] = useState<PersonnelPasswordUpdateProps>({
    current_password: "",
    new_password: "",
    confirm_password: "",
  });

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const { name, value } = e.target;
    setForm({
      ...form,
      [name]: value,
    });
  }

  return (
    <div>
      <div className="details-block-single">
        <div className="text-input">
          <input
            type="password"
            name="current_password"
            value={form.current_password}
            onChange={handleChange}
            placeholder=""
            autoComplete="new-field"
          />
          <label>Current Password</label>
        </div>
      </div>

      <div className="details-block">
        <div className="details-50">
          <div className="text-input">
            <input
              type="password"
              name="new_password"
              value={form.new_password}
              onChange={handleChange}
              placeholder=""
              autoComplete="new-field"
            />
            <label>New Password</label>
          </div>
        </div>

        <div className="details-50">
          <div className="text-input">
            <input
              type="password"
              name="confirm_password"
              value={form.confirm_password}
              onChange={handleChange}
              placeholder=""
              autoComplete="new-field"
            />
            <label>Confirm Password</label>
          </div>
        </div>
      </div>
    </div>
  );
}

export default UpdatePersonnelPassword;
