import type { ReactNode } from "react";

interface PageWrapperProps {
  children: ReactNode;
}

function PageWrapper({ children }: PageWrapperProps) {
  return <div id="content-wrapper">{children}</div>;
}

export default PageWrapper;
