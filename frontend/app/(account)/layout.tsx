import { redirect } from "next/navigation";

import { getPersonnelQuery } from "@/lib/queries/personnel";
import "bootstrap/dist/css/bootstrap.css";
import "@/styles/colour_pallets.scss";
import "@/styles/global.scss";

export default async function AccountGroupLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const userResult = await getPersonnelQuery();

  if (userResult.isErr()) {
    console.log(userResult.error);
    // redirect("/login");
  }

  return <>{children}</>;
}
