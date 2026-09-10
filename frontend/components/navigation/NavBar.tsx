import PageBanner from "../common/banners/PageBanner";
import PageWrapper from "../common/PageWrapper";
import NavBarItem from "./NavBarItem";

interface NavBarProps {
  frontendEnv?: string;
}

export default function NavBar({ frontendEnv = "" }: NavBarProps) {
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
              <NavBarItem name="Personnel" urlPath="/personnel" />
            </div>
          </div>
        </PageWrapper>
      </nav>
      <PageBanner
        message={frontendEnv ? "Environment: " + frontendEnv : "Test"}
        type="INFO"
      />
    </div>
  );
}
