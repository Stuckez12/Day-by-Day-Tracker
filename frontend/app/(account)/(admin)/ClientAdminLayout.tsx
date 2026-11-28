"use client";

import { useRouter } from "next/navigation";
import { type ReactNode, useContext } from "react";

import { PartialPersonnelContext } from "@/components/common/contexts/personnelContext";

interface ClientAdminLayoutProps {
  children: ReactNode;
}

export default function ClientAdminLayout({
  children,
}: ClientAdminLayoutProps) {
  const router = useRouter();
  const { partialPersonnel } = useContext(PartialPersonnelContext);

  if (partialPersonnel.is_admin === false) {
    router.push("/tracker");
    return <></>;
  }

  return (
    <div className="flex flex-col">
      <main>{children}</main>
    </div>
  );
}
