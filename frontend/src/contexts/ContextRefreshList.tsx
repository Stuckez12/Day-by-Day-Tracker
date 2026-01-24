import { createContext } from "react";
import type { Dispatch, SetStateAction } from "react";

interface RefreshContextType {
  refreshList: boolean;
  setRefreshList: Dispatch<SetStateAction<boolean>>;
}

export const ContextRefreshList = createContext<RefreshContextType>({
  refreshList: true,
  setRefreshList: () => {},
});
