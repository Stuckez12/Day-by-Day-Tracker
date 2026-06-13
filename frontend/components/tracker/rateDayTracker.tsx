import { useContext } from "react";
import RateDayButton from "@/components/common/buttons/rateDayButton";
import { RankingUIContext } from "@/components/tracker/rateDayContext";

interface RateDayTrackerProps {}

export default function RateDayTracker({}: RateDayTrackerProps) {
  const { refreshRanking } = useContext(RankingUIContext);

  return (
    <div className="rating-button-bar">
      <RateDayButton ranking={0} current_rank={refreshRanking.ranking} />
      <RateDayButton ranking={1} current_rank={refreshRanking.ranking} />
      <RateDayButton ranking={2} current_rank={refreshRanking.ranking} />
      <RateDayButton ranking={3} current_rank={refreshRanking.ranking} />
      <RateDayButton ranking={4} current_rank={refreshRanking.ranking} />
      <RateDayButton ranking={5} current_rank={refreshRanking.ranking} />
      <RateDayButton ranking={6} current_rank={refreshRanking.ranking} />
      <RateDayButton ranking={7} current_rank={refreshRanking.ranking} />
      <RateDayButton ranking={8} current_rank={refreshRanking.ranking} />
      <RateDayButton ranking={9} current_rank={refreshRanking.ranking} />
      <RateDayButton ranking={10} current_rank={refreshRanking.ranking} />
    </div>
  );
}
