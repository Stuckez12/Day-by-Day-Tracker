"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import SideNavBar from "@/components/navigation/SideNavBar";
import { getPersonnelQuery } from "@/lib/queries/personnel";

import "bootstrap/dist/css/bootstrap.css";
import "@/styles/colour_pallets.scss";
import "@/styles/global.scss";

export default function AccountGroupLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const router = useRouter();
  const [checkedUser, setCheckedUser] = useState(false);

  useEffect(() => {
    async function isUserLoggedIn() {
      const userResult = await getPersonnelQuery();

      setCheckedUser(true);

      if (userResult.isErr()) {
        console.log("Redirect to login");
        console.log(userResult.error);
        router.push("/login");
      }
    }

    isUserLoggedIn();
  }, []);

  if (!checkedUser) {
    return <></>;
  }

  // return <>{children}</>;
  return (
    <SideNavBar>
      <></>
    </SideNavBar>
  );
}
