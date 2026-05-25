import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

import PageWrapper from "components/common/PageWrapper";
import WelcomeText from "components/common/WelcomeText";

import ContextLandingPage from "components/rating/ContextLandingPage";

import { is_logged_in } from "scripts/auth/is_login.ts";

function LandingPage() {
  const navigate = useNavigate();

  useEffect(() => {
    is_logged_in(navigate);
  }, [navigate]);

  return (
    <PageWrapper>
      <h1>Landing Page</h1>
      <WelcomeText />
      <ContextLandingPage />
    </PageWrapper>
  );
}

export default LandingPage;
