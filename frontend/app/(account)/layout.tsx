"use client";

import { useRouter } from "next/navigation";
import { useContext, useEffect, useState } from "react";

import SideNavBar from "@/components/navigation/SideNavBar";
import { getPersonnelQuery } from "@/lib/queries/personnel";

import "bootstrap/dist/css/bootstrap.css";
import "@/styles/colour_pallets.scss";
import "@/styles/global.scss";
import { PartialPersonnelContext } from "@/components/common/contexts/personnelContext";

export default function AccountGroupLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const router = useRouter();
  const [checkedUser, setCheckedUser] = useState(false);
  const { setPartialPersonnel } = useContext(PartialPersonnelContext);

  useEffect(() => {
    async function isUserLoggedIn() {
      const userResult = await getPersonnelQuery();

      setCheckedUser(true);

      if (!userResult.ok) {
        console.log("Redirect to login");
        console.log(userResult.error);
        router.push("/login");

        return;
      }

      setPartialPersonnel(userResult.data);
    }

    isUserLoggedIn();
  }, [checkedUser, setPartialPersonnel, router]);

  if (!checkedUser) {
    return <></>;
  }

  return <SideNavBar>{children}</SideNavBar>;
}
