"use client";

import { useRouter } from "next/navigation";
import { useContext, useEffect } from "react";
import { useSession } from "next-auth/react";

import { getPersonnelQuery } from "@/lib/queries/personnel";
import { getAccessToken } from "@/lib/common/auth/getAccessToken";

import "@/styles/colour_pallets.scss";
import { PartialPersonnelContext } from "@/components/common/contexts/personnelContext";
import NavBar from "@/components/navigation/NavBar";
import PageWrapper from "@/components/common/PageWrapper";

export default function AccountGroupLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const router = useRouter();
  const { data: _session, status } = useSession();
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

  return (
    <div className="flex flex-col">
      <NavBar />
      <main>{children}</main>
    </div>
  );
}
