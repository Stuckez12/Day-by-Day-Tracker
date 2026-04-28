import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

import PageWrapper from "components/common/PageWrapper";
import WelcomeText from "components/common/WelcomeText";
import RatingBar from "components/rating/RatingBar";

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
      <RatingBar />
    </PageWrapper>
  );
}

export default LandingPage;
