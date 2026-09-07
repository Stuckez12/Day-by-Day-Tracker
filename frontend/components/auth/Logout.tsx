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
      className="my-4 w-full rounded-lg bg-[#007ea7] py-1 text-center text-white hover:bg-[#00a1d6] active:bg-[#00a8e8]"
      onClick={onSubmit}
    >
      Logout
    </button>
  );
}

export default Logout;
