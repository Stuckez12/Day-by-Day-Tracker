import { ReactNode } from "react";

import "@/styles/common/navigation.scss";

interface SideNavItemProps {
  icon: ReactNode;
  name: string;
}

export default function SideNavItem({ icon, name }: SideNavItemProps) {
  return (
    <div className="side-nav-item-container">
      {icon}
      <div className="text-container">
        <p>{name}</p>
      </div>
    </div>
  );
}
