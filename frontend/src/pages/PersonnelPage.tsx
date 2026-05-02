import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import PageWrapper from "components/common/PageWrapper";
import UpdatePersonnelDetails from "components/personnel/UpdatePersonnelDetails";
import UpdatePersonnelEmail from "components/personnel/UpdatePersonnelEmail";
import UpdatePersonnelPassword from "components/personnel/UpdatePersonnelPassword";
import Logout from "components/personnel/Logout";

import type { PersonnelProps } from "interfaces/personnel";

import { ContextPersonnelForms } from "contexts/ContextPersonnelForms";

import type { PersonnelPropsContext } from "interfaces/personnel";

import APICall from "scripts/api.ts";
import { is_logged_in } from "scripts/auth/is_login.ts";

function PersonnelPage() {
  const navigate = useNavigate();

  const [refreshPersonnelForms, setRefreshPersonnelForms] =
    useState<PersonnelPropsContext>({
      id: "",
      first_name: "",
      last_name: "",
      email: "",
    });

  useEffect(() => {
    let result = is_logged_in(navigate);

    if (!result) {
      return;
    }

    async function fetch_personnel() {
      const [success, data, message] =
        await APICall.get<PersonnelProps>("/personal/me");

      if (success) {
        console.log("Success. Now refresh");
        console.log(data);
        setRefreshPersonnelForms(data!);
        console.log(refreshPersonnelForms);
      } else {
        console.log("Error when getting data");
        console.log(message);
      }
    }

    fetch_personnel();
  }, [navigate]);

  return (
    <PageWrapper>
      <ContextPersonnelForms.Provider
        value={{ refreshPersonnelForms, setRefreshPersonnelForms }}
      >
        <UpdatePersonnelDetails />
        <UpdatePersonnelEmail />
        <UpdatePersonnelPassword />
      </ContextPersonnelForms.Provider>
      <Logout />
    </PageWrapper>
  );
}

export default PersonnelPage;
