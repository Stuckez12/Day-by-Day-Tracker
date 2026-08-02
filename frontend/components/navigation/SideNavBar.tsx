import { ReactNode } from "react";

import "@/styles/common/navigation.scss";

interface SideNavBarProps {
  children: ReactNode;
}

import SideNavItem from "./SideNavItem";

export default function SideNavBar({ children }: SideNavBarProps) {
  return (
    <div className="web-page-container">
      <div className="side-nav-container">
        <div className="nav-item-group-container">
          <SideNavItem name="Tracker" redirection="/tracker" />
          <SideNavItem name="Rankings" redirection="/ranking" />
          <SideNavItem name="Personnel" redirection="/personnel" />
        </div>
        <div className="nav-item-group-container lower-side-nav-block"></div>
      </div>
      <div className="main-content-container">{children}</div>
    </div>
  );
}
