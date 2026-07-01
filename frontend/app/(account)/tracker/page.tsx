"use client";

import { useEffect, useState } from "react";

import DisplayRankingToday from "@/components/tracker/displayRankingData";
import { RankingTrackerContext } from "@/components/tracker/rateDayContext";
import RateDayText from "@/components/tracker/rateDayText";
import RateDayTracker from "@/components/tracker/rateDayTracker";
import { RankingUIDataProp } from "@/lib/interfaces/ranking";
import { getRankTodayQuery } from "@/lib/queries/ranking";

export default function TrackerPage() {
  const [refreshRanking, setRefreshRanking] = useState<RankingUIDataProp>({
    day: "",
    ranking: undefined,

    text_events: undefined,
    text_notes: undefined,
  });

  useEffect(() => {
    async function fetchRank() {
      const result = await getRankTodayQuery();

      if (result.ok) {
        setRefreshRanking(result.data);
      } else {
        console.log("Error when getting data");
        console.log(result.error);
      }
    }
    fetchRank();
  }, []);

  return (
    <div className="page-wrapper">
      <div className="tracker-container">
        <RankingTrackerContext.Provider
          value={{ refreshRanking, setRefreshRanking }}
        >
          <DisplayRankingToday />
          <RateDayTracker />
          <RateDayText />
        </RankingTrackerContext.Provider>
      </div>
    </div>
  );
}
