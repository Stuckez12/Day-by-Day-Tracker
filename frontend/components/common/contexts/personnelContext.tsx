import { createContext, Dispatch, SetStateAction } from "react";

import { PartialPersonnelProp } from "@/lib/interfaces/personnel";

interface ContextType {
  partialPersonnel: PartialPersonnelProp;
  setPartialPersonnel: Dispatch<SetStateAction<PartialPersonnelProp>>;
}

export const PartialPersonnelContext = createContext<ContextType>({
  partialPersonnel: {
    id: undefined,
    created_at: undefined,
    updated_at: undefined,

    email: undefined,
    password: undefined,

    first_name: undefined,
    last_name: undefined,
  },
  setPartialPersonnel: () => {},
});
