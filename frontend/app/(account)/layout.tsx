import NavBar from "@/components/navigation/NavBar";
import ClientAccountLayout from "./ClientAccountLayout";

export const dynamic = "force-dynamic";

export default function AccountGroupLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  let banner = "";
  const isTestProd = process.env.IS_TEST_PROD ?? "false";

  if (process.env.NODE_ENV === "development")
    banner = "Application is in development mode";
  else if (isTestProd === "true")
    banner = "Application is deployed only as a showcase";

  return (
    <ClientAccountLayout nav={<NavBar pageBanner={banner} />}>
      {children}
    </ClientAccountLayout>
  );
}
