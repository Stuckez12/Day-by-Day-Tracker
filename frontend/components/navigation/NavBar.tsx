"use client";

import { useContext } from "react";
import PageBanner from "../common/banners/PageBanner";
import { PartialPersonnelContext } from "../common/contexts/personnelContext";
import PageWrapper from "../common/PageWrapper";
import NavBarItem from "./NavBarItem";

interface NavBarProps {
  pageBanner?: string;
}

export default function NavBar({ pageBanner = "" }: NavBarProps) {
  const { partialPersonnel } = useContext(PartialPersonnelContext);

  return (
    <div className="mb-4">
      <nav className="bg-secondary py-1">
        <PageWrapper>
          <div className="flex flex-row w-full">
            <div className="mr-auto flex flex-row space-x-1">
              <NavBarItem name="Tracker" urlPath="/tracker" />
              <NavBarItem name="Rankings" urlPath="/ranking" />
            </div>
            <div className="flex flex-row space-x-1">
              {partialPersonnel.is_admin === true && (
                <NavBarItem name="Admin" urlPath="/application-management" />
              )}

              <NavBarItem name="Personnel" urlPath="/personnel" />
            </div>
          </div>
        </PageWrapper>
      </nav>
      <PageBanner message={pageBanner ? pageBanner : ""} type="INFO" />
    </div>
  );
}
