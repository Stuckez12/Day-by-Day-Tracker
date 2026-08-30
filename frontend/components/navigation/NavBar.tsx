import NavBarItem from "./NavBarItem";

export default function NavBar() {
  return (
    <nav className="flex flex-row w-full mb-4">
      <div className="mr-auto flex flex-row space-x-4">
        <NavBarItem name="Tracker" urlPath="/tracker" />
        <NavBarItem name="Rankings" urlPath="/ranking" />
      </div>
      <div className="flex flex-row space-x-4">
        <NavBarItem name="Personnel" urlPath="/personnel" />
      </div>
    </nav>
  );
}
