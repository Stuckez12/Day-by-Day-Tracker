import Link from "next/link";

interface NavBarItemProps {
  name: string;
  urlPath: string;
}

export default function NavBarItem({ name, urlPath }: NavBarItemProps) {
  return (
    <Link
      href={urlPath}
      className="items-center px-2.5 py-2 text-lg font-bold no-underline! text-white"
    >
      {name}
    </Link>
  );
}
