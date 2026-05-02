import { useState } from "react";

import type {
  PersonnelPasswordUpdateProps,
  PersonnelProps,
} from "interfaces/personnel";

import APICall from "scripts/api.ts";

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

  function onSubmit(e: React.MouseEvent<HTMLButtonElement>) {
    e.preventDefault();

    console.log("Form data:", form);

    async function update_password(form: PersonnelPasswordUpdateProps) {
      const [success, _data, message] = await APICall.put<PersonnelProps>(
        "/personal/me/password",
        {
          current_password: form.current_password,
          new_password: form.new_password,
        },
      );

      if (success) {
        console.log("Success");
      } else {
        console.log("Error when getting data");
        console.log(message);
      }
    }

    update_password(form);
  }

  return (
    <>
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

      <button className="submit-button" onClick={onSubmit}>
        Submit
      </button>
    </>
  );
}

export default UpdatePersonnelPassword;
