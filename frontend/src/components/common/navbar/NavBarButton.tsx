import { Link } from "react-router-dom";

interface NavBarButtonProps {
  frontend_url: string;
  display_text: string;
}

function NavBarButton({ frontend_url, display_text }: NavBarButtonProps) {
  return (
    <li>
      <Link to={frontend_url}>{display_text}</Link>
    </li>
  );
}

export default NavBarButton;
