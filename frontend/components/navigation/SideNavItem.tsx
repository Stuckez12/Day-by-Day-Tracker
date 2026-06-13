import { ReactNode } from "react";
import Link from "next/link";

import "@/styles/common/navigation.scss";

interface SideNavItemProps {
  icon: ReactNode;
  name: string;
  redirection: string;
}

export default function SideNavItem({ name, redirection }: SideNavItemProps) {
  return (
    <Link href={redirection}>
      <div className="side-nav-item-container">
        {/* <div className="icon-container">{icon}</div> */}
        <div className="text-container">{name}</div>
      </div>
    </Link>
  );
}
