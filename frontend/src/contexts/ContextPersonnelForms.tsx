import { createContext } from "react";
import type { Dispatch, SetStateAction } from "react";

import type { PersonnelPropsContext } from "interfaces/personnel";

interface ContextType {
  refreshPersonnelForms: PersonnelPropsContext;
  setRefreshPersonnelForms: Dispatch<SetStateAction<PersonnelPropsContext>>;
}

export const ContextPersonnelForms = createContext<ContextType>({
  refreshPersonnelForms: { id: "", first_name: "", last_name: "", email: "" },
  setRefreshPersonnelForms: () => {},
});
