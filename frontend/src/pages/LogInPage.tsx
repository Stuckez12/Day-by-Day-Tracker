import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

import LogInForm from "components/auth/login/LogInForm";
import PageWrapper from "components/common/PageWrapper";

import { check_logged_in } from "scripts/auth/is_login.ts";

function LogInPage() {
  const navigate = useNavigate();

  useEffect(() => {
    check_logged_in(navigate);
  }, []);

  return (
    <PageWrapper>
      <LogInForm />
    </PageWrapper>
  );
}

export default LogInPage;
