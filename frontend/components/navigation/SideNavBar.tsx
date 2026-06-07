import { ReactNode } from "react";

import "@/styles/common/navigation.scss";

interface SideNavBarProps {
  children: ReactNode;
}

import Logo from "@/assets/svg/star.svg";
import SideNavItem from "./SideNavItem";

export default function SideNavBar({ children }: SideNavBarProps) {
  return (
    <div className="side-nav-container">
      <div className="nav-item-group-container">
        <SideNavItem icon={<Logo className="icon" />} name="Test" />
      </div>
      <div className="nav-item-group-container lower-side-nav-block"></div>
    </div>
  );
}
