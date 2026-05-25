import { createContext } from "react";
import type { Dispatch, SetStateAction } from "react";

import type { RankingProps } from "interfaces/ranking";

interface ContextType {
  refreshRankingLanding: RankingProps;
  setRefreshRankingLanding: Dispatch<SetStateAction<RankingProps>>;
}

export const ContextLanding = createContext<ContextType>({
  refreshRankingLanding: {
    id: "",
    personal_id: "",

    day: "",
    ranking: -1,

    text_events: "",
    text_notes: "",

    created_at: "",
    updated_at: "",
  },
  setRefreshRankingLanding: () => {},
});
