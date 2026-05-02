import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

import PageWrapper from "components/common/PageWrapper";
import UpdatePersonnelDetails from "components/personnel/UpdatePersonnelDetails";
import UpdatePersonnelEmail from "components/personnel/UpdatePersonnelEmail";
import UpdatePersonnelPassword from "components/personnel/UpdatePersonnelPassword";
import Logout from "components/personnel/Logout";

import { is_logged_in } from "scripts/auth/is_login.ts";

function PersonnelPage() {
  const navigate = useNavigate();

  useEffect(() => {
    is_logged_in(navigate);
  }, [navigate]);

  return (
    <PageWrapper>
      <UpdatePersonnelDetails />
      <UpdatePersonnelEmail />
      <UpdatePersonnelPassword />
      <Logout />
    </PageWrapper>
  );
}

export default PersonnelPage;
