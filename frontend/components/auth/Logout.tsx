"use client";

import { useRouter } from "next/navigation";
import { signOut } from "next-auth/react";

function Logout() {
  const router = useRouter();

  function onSubmit(e: React.MouseEvent<HTMLButtonElement>) {
    e.preventDefault();

    signOut({ redirect: false }).then(() => router.replace("/login"));
  }

  return (
    <button
      className="my-4 w-full rounded-lg bg-button py-1 text-center text-inverted-text-color hover:bg-button-hover active:bg-button-clicked"
      onClick={onSubmit}
    >
      Logout
    </button>
  );
}

export default Logout;
