import ClientAdminLayout from "./ClientAdminLayout";

export default function AccountGroupLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return <ClientAdminLayout>{children}</ClientAdminLayout>;
}
