import "bootstrap/dist/css/bootstrap.min.css";
import "@/styles/colour_pallets.scss";
import "@/styles/common/form.scss";
import "@/styles/global.scss";
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
