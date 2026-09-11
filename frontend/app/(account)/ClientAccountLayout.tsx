"use client";

import { getAccessToken } from "@/lib/common/auth/getAccessToken";
import { getPersonnelQuery } from "@/lib/queries/personnel";
import { useRouter } from "next/navigation";
import { useContext, useEffect, type ReactNode } from "react";
import { useSession } from "next-auth/react";

import { PartialPersonnelContext } from "@/components/common/contexts/personnelContext";

interface ClientAccountLayoutProps {
  children: ReactNode;
  nav: ReactNode;
}

export default function ClientAccountLayout({
  children,
  nav,
}: ClientAccountLayoutProps) {
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
      {nav}
      <main>{children}</main>
    </div>
  );
}
