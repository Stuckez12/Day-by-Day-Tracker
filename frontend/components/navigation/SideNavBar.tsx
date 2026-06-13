import { ReactNode } from "react";

import "@/styles/common/navigation.scss";

interface SideNavBarProps {
  children: ReactNode;
}

import StarSVG from "@/assets/svg/star";
import SideNavItem from "./SideNavItem";

export default function SideNavBar({ children }: SideNavBarProps) {
  return (
    <div className="web-page-container">
      <div className="side-nav-container">
        <div className="nav-item-group-container">
          <SideNavItem
            icon={<StarSVG />}
            name="Tracker"
            redirection="/tracker"
          />
          <SideNavItem
            icon={<StarSVG />}
            name="Rankings"
            redirection="/ranking"
          />
        </div>
        <div className="nav-item-group-container lower-side-nav-block"></div>
      </div>
      <div className="main-content-container">{children}</div>
    </div>
  );
}
