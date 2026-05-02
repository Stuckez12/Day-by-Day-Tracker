import { useNavigate } from "react-router-dom";
import type { NavigateFunction } from "react-router-dom";

import APICall from "scripts/api.ts";

import "styles/auth/login-form.scss";
import "styles/pages/personnel.scss";

function Logout() {
  const navigate = useNavigate();

  function onSubmit(e: React.MouseEvent<HTMLButtonElement>) {
    e.preventDefault();

    async function logout(navigate_func: NavigateFunction) {
      const [success, _data, message] = await APICall.post<null>(
        "/auth/logout",
        {},
      );

      if (success) {
        console.log("Success. Redirecting");
        navigate_func("/login", { replace: true });
      } else {
        console.log("Error when getting data");
        console.log(message);
      }
    }

    logout(navigate);
  }

  return (
    <button className="submit-button" onClick={onSubmit}>
      Logout
    </button>
  );
}

export default Logout;
