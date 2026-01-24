import { createContext } from "react";
import type { Dispatch, SetStateAction } from "react";

interface RefreshContextType {
  refreshList: boolean;
  setRefreshList: Dispatch<SetStateAction<boolean>>;
}

export const ContextRefreshPersonnelList = createContext<RefreshContextType>({
  refreshList: true,
  setRefreshList: () => {},
});
