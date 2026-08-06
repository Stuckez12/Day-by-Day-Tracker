import { RankingUIDataProp } from "@/lib/interfaces/ranking";
import { createContext, Dispatch, SetStateAction } from "react";

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
