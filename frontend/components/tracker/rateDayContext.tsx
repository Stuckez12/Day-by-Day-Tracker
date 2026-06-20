import { createContext, Dispatch, SetStateAction } from "react";

import { RankingUIDataProp } from "@/lib/interfaces/ranking";

interface ContextType {
  refreshRanking: RankingUIDataProp;
  setRefreshRanking: Dispatch<SetStateAction<RankingUIDataProp>>;
}

export const RankingTrackerContext = createContext<ContextType>({
  refreshRanking: {
    day: "",
    ranking: undefined,
    text_events: undefined,
    text_notes: undefined,
  },
  setRefreshRanking: () => {},
});
