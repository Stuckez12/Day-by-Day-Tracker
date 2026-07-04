"use client";

import { useRouter } from "next/navigation";
import { personnelLogoutQuery } from "@/lib/queries/auth";

import "@/styles/forms/login-form.scss";

function Logout() {
  const router = useRouter();

  function onSubmit(e: React.MouseEvent<HTMLButtonElement>) {
    e.preventDefault();

    async function logout() {
      const result = await personnelLogoutQuery();

      if (result.ok) {
        console.log("Success. Logged out");
        router.push("/login");
      } else {
        console.log("Error when logging out");
        console.log(result.error);
      }
    }

    logout();
  }

  return (
    <button className="submit-button" onClick={onSubmit}>
      Logout
    </button>
  );
}

export default Logout;
