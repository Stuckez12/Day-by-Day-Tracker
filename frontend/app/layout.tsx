import "@/styles/global.css";
import ClientLayout from "./ClientLayout";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html>
      <body data-theme="base">
        <ClientLayout>{children}</ClientLayout>
      </body>
    </html>
  );
}
