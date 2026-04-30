import "styles/auth/login-form.scss";

function UpdatePersonnelDetails() {
  return (
    <div>
      <div className="text-input">
        <input
          type="text"
          name="first_name"
          value="{form.first_name}"
          //   onChange={handleChange}
          placeholder=""
          autoComplete="new-field"
        />
        <label>First Name</label>
      </div>

      <div className="text-input">
        <input
          type="text"
          name="last_name"
          value="{form.last_name}"
          //   onChange={handleChange}
          placeholder=""
          autoComplete="new-field"
        />
        <label>Last Name</label>
      </div>
    </div>
  );
}

export default UpdatePersonnelDetails;
