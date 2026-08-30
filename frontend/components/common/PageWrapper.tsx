import clsx from "clsx";
import { ReactNode } from "react";

interface PageWrapperProps {
  children: ReactNode;
}

export default function PageWrapper({ children }: PageWrapperProps) {
  return (
    <div
      className={clsx(
        "mx-auto box-border w-full max-w-360 px-4", // Default
        "min-[577px]:px-16!", // Small Screens
      )}
    >
      {children}
    </div>
  );
}
