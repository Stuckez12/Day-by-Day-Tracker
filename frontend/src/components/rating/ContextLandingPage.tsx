import { useEffect, useState } from "react";

import TextInputs from "components/common/TextInputs";
import RatingBar from "components/rating/RatingBar";

import { ContextLanding } from "contexts/ContextLanding";

import type { RankingProps } from "interfaces/ranking";

import APICall from "scripts/api.ts";

function ContextLandingPage() {
  const [refreshRankingLanding, setRefreshRankingLanding] = useState({
    id: "",
    personal_id: "",

    day: "",
    ranking: -1,

    text_events: "",
    text_notes: "",

    created_at: "",
    updated_at: "",
  });

  useEffect(() => {
    async function fetchRank() {
      const [success, response, message] =
        await APICall.get<RankingProps>("/ranking/today");

      if (success) {
        setRefreshRankingLanding(response!);
      } else {
        console.log("Error when getting data");
        console.log(message);
      }
    }
    fetchRank();
  }, []);

  return (
    <ContextLanding.Provider
      value={{ refreshRankingLanding, setRefreshRankingLanding }}
    >
      <RatingBar />
      <TextInputs />
    </ContextLanding.Provider>
  );
}

export default ContextLandingPage;
