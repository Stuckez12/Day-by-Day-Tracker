import PageWrapper from "../common/PageWrapper";
import NavBarItem from "./NavBarItem";

export default function NavBar() {
  return (
    <nav className="bg-app-primary mb-4 py-1">
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
  );
}
