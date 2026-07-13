"use client";

import { useRouter } from "next/navigation";
import { signOut } from "next-auth/react";

import "@/styles/forms/login-form.scss";

function Logout() {
  const router = useRouter();

  function onSubmit(e: React.MouseEvent<HTMLButtonElement>) {
    e.preventDefault();

    signOut({ redirect: false }).then(() => router.replace("/login"));
  }

  return (
    <button className="submit-button" onClick={onSubmit}>
      Logout
    </button>
  );
}

export default Logout;
