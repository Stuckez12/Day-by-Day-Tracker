import { Link } from "react-router-dom";

interface NavBarButtonProps {
  frontend_url: string;
  display_text: string;
  right_hand_side?: boolean;
}

function NavBarButton({
  frontend_url,
  display_text,
  right_hand_side,
}: NavBarButtonProps) {
  var float_dir = "left";

  if (right_hand_side !== undefined) {
    float_dir = "right";
  }

  return (
    <li className={float_dir}>
      <Link to={frontend_url}>{display_text}</Link>
    </li>
  );
}

export default NavBarButton;
