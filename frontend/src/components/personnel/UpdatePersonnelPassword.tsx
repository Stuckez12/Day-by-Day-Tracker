import "styles/auth/login-form.scss";

function UpdatePersonnelPassword() {
  return (
    <div>
      <div className="text-input">
        <input
          type="text"
          name="current_password"
          value="{form.current_password}"
          //   onChange={handleChange}
          placeholder=""
          autoComplete="new-field"
        />
        <label>Current Password</label>
      </div>

      <div className="text-input">
        <input
          type="text"
          name="new_password"
          value="{form.new_password}"
          //   onChange={handleChange}
          placeholder=""
          autoComplete="new-field"
        />
        <label>New Password</label>
      </div>

      <div className="text-input">
        <input
          type="text"
          name="confirm_password"
          value="{form.confirm_password}"
          //   onChange={handleChange}
          placeholder=""
          autoComplete="new-field"
        />
        <label>Confirm Password</label>
      </div>
    </div>
  );
}

export default UpdatePersonnelPassword;
