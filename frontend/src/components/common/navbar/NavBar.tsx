import { useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import PageWrapper from "components/common/PageWrapper";
import NavBarButton from "components/common/navbar/NavBarButton.tsx";
import Message from "components/Message";
import MenuSVG from "components/svg/menu.tsx";

import LogInPage from "pages/LogInPage";
import LandingPage from "pages/LandingPage";
import PersonnelPage from "pages/PersonnelPage";
import RankingPage from "pages/RankingPage";

import "styles/navbar.scss";

function NavBar() {
  const [navbarState, setNavbarState] = useState<boolean>(false);

  function toggle_navbar() {
    if (navbarState) setNavbarState(false);
    else setNavbarState(true);
  }

  return (
    <Router>
      <nav id="navigation-bar">
        <PageWrapper>
          <ul className={`nav-list ${navbarState ? "dropdown" : ""}`}>
            <NavBarButton frontend_url="/" display_text="Tracker" />
            <NavBarButton frontend_url="/rates" display_text="Rates" />
            <NavBarButton frontend_url="/tasks" display_text="Tasks" />
            <NavBarButton frontend_url="/stats" display_text="Stats" />
            <NavBarButton
              frontend_url="/personnel"
              display_text="Personnel"
              right_hand_side={true}
            />
            <li className="nav-toggle right" onClick={() => toggle_navbar()}>
              <MenuSVG />
            </li>
          </ul>
        </PageWrapper>
      </nav>

      <Routes>
        <Route path="/login" element={<LogInPage />} />
        <Route path="/" element={<LandingPage />} />
        <Route path="/rates" element={<RankingPage />} />
        <Route path="/tasks" element={<Message text="Tasks" />} />
        <Route path="/stats" element={<Message text="Stats" />} />
        <Route path="/personnel" element={<PersonnelPage />} />
      </Routes>
    </Router>
  );
}

export default NavBar;
