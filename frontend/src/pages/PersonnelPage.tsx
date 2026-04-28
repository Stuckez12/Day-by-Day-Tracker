import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

import PageWrapper from "components/common/PageWrapper";
import ContextPersonnelList from "components/personnel/ContextPersonnelList";

import { is_logged_in } from "scripts/auth/is_login.ts";

function PersonnelPage() {
  const navigate = useNavigate();

  useEffect(() => {
    is_logged_in(navigate);
  }, [navigate]);

  return (
    <PageWrapper>
      <ContextPersonnelList />
    </PageWrapper>
  );
}

export default PersonnelPage;
