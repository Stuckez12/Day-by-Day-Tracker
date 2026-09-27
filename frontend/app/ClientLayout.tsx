"use client";

import { SessionProvider } from "next-auth/react";
import { useState } from "react";

import { PartialPersonnelContext } from "@/components/common/contexts/personnelContext";
import { PartialPersonnelProp } from "@/lib/interfaces/personnel";

export default function ClientLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [partialPersonnel, setPartialPersonnel] =
    useState<PartialPersonnelProp>({
      id: undefined,
      created_at: undefined,
      updated_at: undefined,
      email: undefined,
      password: undefined,
      first_name: undefined,
      last_name: undefined,
    });

  return (
    <SessionProvider>
      <PartialPersonnelContext.Provider
        value={{ partialPersonnel, setPartialPersonnel }}
      >
        {children}
      </PartialPersonnelContext.Provider>
    </SessionProvider>
  );
}
