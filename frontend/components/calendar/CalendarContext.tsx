import { createContext, Dispatch, SetStateAction } from "react";

import { RankingUIDataProp } from "@/lib/interfaces/ranking";

interface ContextType {
  ranking: RankingUIDataProp;
  setRanking: Dispatch<SetStateAction<RankingUIDataProp>>;
}

export const CalendarContext = createContext<ContextType>({
  ranking: {
    day: "",
    ranking: undefined,
    text_events: undefined,
    text_notes: undefined,
  },
  setRanking: () => {},
});
