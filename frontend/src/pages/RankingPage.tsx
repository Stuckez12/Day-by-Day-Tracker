import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

import PageWrapper from "components/common/PageWrapper";
import ContextRatingList from "components/rating/ContextRatingList";

import { is_logged_in } from "scripts/auth/is_login.ts";

function RankingPage() {
  const navigate = useNavigate();

  useEffect(() => {
    is_logged_in(navigate);
  }, []);

  return (
    <PageWrapper>
      <ContextRatingList />
    </PageWrapper>
  );
}

export default RankingPage;
