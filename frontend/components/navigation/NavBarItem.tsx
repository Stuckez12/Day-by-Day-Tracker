import Link from "next/link";

interface NavBarItemProps {
  name: string;
  urlPath: string;
}

export default function NavBarItem({ name, urlPath }: NavBarItemProps) {
  return (
    <Link href={urlPath}>
      <div className="items-center p-2 bg-red-800">
        <p className="m-0">{name}</p>
      </div>
    </Link>
  );
}
