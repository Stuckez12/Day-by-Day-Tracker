import "styles/auth/login-form.scss";

function UpdatePersonnelEmail() {
  return (
    <div>
      <div className="text-input">
        <input
          type="text"
          name="email"
          value="{form.email}"
          //   onChange={handleChange}
          placeholder=""
          autoComplete="new-field"
        />
        <label>Email</label>
      </div>
    </div>
  );
}

export default UpdatePersonnelEmail;
