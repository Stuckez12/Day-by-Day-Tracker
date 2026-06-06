import type { Metadata } from "next";

import "bootstrap/dist/css/bootstrap.css";
import "@/styles/colour_pallets.scss";
import "@/styles/global.scss";

export const metadata: Metadata = {
  title: "DbD Tracker",
  description: "Web app to track the day",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html>
      <body data-theme="base">{children}</body>
    </html>
  );
}
