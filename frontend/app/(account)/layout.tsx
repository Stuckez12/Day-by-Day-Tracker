import NavBar from "@/components/navigation/NavBar";
import ClientAccountLayout from "./ClientAccountLayout";

export const dynamic = "force-dynamic";

export default function AccountGroupLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <ClientAccountLayout
      nav={<NavBar frontendEnv={process.env.FRONTEND_ENV ?? ""} />}
    >
      {children}
    </ClientAccountLayout>
  );
}
