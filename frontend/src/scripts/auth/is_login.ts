import type { NavigateFunction } from "react-router-dom";

import type { PersonnelRowProps } from "interfaces/personnel.ts";

import APICall from "scripts/api.ts";

export async function check_logged_in(navigate_func: NavigateFunction) {
  const [success] = await APICall.get<PersonnelRowProps>("/personal/me");

  if (success) {
    console.log("Success. Now redirect");
    navigate_func("/", { replace: true });
  }
}

export async function is_logged_in(navigate_func: NavigateFunction) {
  const [success] = await APICall.get<PersonnelRowProps>("/personal/me");

  if (!success) {
    navigate_func("/login", { replace: true });
    return false;
  }

  return true;
}
