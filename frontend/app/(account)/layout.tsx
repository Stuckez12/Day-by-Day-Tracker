"use client";

import { useRouter } from "next/navigation";
import { useContext, useEffect } from "react";
import { useSession } from "next-auth/react";

import SideNavBar from "@/components/navigation/SideNavBar";
import { getPersonnelQuery } from "@/lib/queries/personnel";
import { getAccessToken } from "@/lib/common/auth/getAccessToken";

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
  const { data: session, status } = useSession();
  const { setPartialPersonnel } = useContext(PartialPersonnelContext);

  useEffect(() => {
    async function loadPersonnel() {
      if (status !== "authenticated") {
        return;
      }

      const accessToken = await getAccessToken();

      if (!accessToken) {
        router.replace("/login");
        return;
      }

      const userResult = await getPersonnelQuery();

      if (!userResult.ok) {
        router.push("/login");
        return;
      }

      setPartialPersonnel(userResult.data);
    }

    if (status === "unauthenticated") {
      router.replace("/login");
      return;
    }

    loadPersonnel();
  }, [setPartialPersonnel, router, status]);

  if (status !== "authenticated") {
    return <></>;
  }

  return <SideNavBar>{children}</SideNavBar>;
}
