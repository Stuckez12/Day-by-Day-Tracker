"use client";

import "bootstrap/dist/css/bootstrap.css";
import "@/styles/colour_pallets.scss";
import "@/styles/common/form.scss";
import "@/styles/global.scss";
import { PartialPersonnelContext } from "@/components/common/contexts/personnelContext";
import { PartialPersonnelProp } from "@/lib/interfaces/personnel";
import { useState } from "react";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
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
    <html>
      <PartialPersonnelContext.Provider
        value={{ partialPersonnel, setPartialPersonnel }}
      >
        <body data-theme="base">{children}</body>
      </PartialPersonnelContext.Provider>
    </html>
  );
}
