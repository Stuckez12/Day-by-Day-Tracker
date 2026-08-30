import { ReactNode } from "react";

interface PageWrapperProps {
  children: ReactNode;
}

export default function PageWrapper({ children }: PageWrapperProps) {
  return (
    <div className="mx-auto box-border w-full max-w-360 px-2 min-[577px]:px-16!">
      {children}
    </div>
  );
}
