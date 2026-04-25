import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import type { LogInProps } from "interfaces/login";
import type { PersonnelRowProps } from "interfaces/personnel.ts";

import APICall from "scripts/api.ts";

import "styles/auth/login-form.scss";

function LogInForm() {
  const navigate = useNavigate();
  const [form, setForm] = useState<LogInProps>({
    email: "",
    password: "",
  });

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const { name, value } = e.target;
    setForm({
      ...form,
      [name]: value,
    });
  }

  async function check_logged_in() {
    const [success] = await APICall.get<PersonnelRowProps>("/personal/me");

    if (success) {
      console.log("Success. Now redirect");
      // navigate("/", { replace: true });
    }
  }

  function onSubmit(e: React.MouseEvent<HTMLButtonElement>) {
    e.preventDefault();

    console.log("Form data:", form);

    async function log_in(form: LogInProps) {
      const [success] = await APICall.post<null>("/auth/login", {
        email: form.email,
        password: form.password,
      });

      if (success) {
        console.log("Success. Now redirect");
        navigate("/", { replace: true });
      } else {
        console.log("Error when logging in");
      }
    }

    log_in(form);
  }

  useEffect(() => {
    check_logged_in();
  }, []);

  return (
    <div className="login-form-container">
      <div className="login-form">
        <label>Log In</label>

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

        <div className="text-input">
          <input
            type="password"
            name="password"
            value={form.password}
            onChange={handleChange}
            placeholder=""
            autoComplete="new-field"
          />
          <label>Password</label>
        </div>

        <button className="submit-button" onClick={onSubmit}>
          Submit
        </button>
      </div>
    </div>
  );
}

export default LogInForm;
