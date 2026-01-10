import type { OptionalRankingProps } from "interfaces/ranking";

function RatingToday(ranking: OptionalRankingProps) {
  if (ranking.ranking == null) return <h1>You have not yet rated today</h1>;

  return <h1>You have rated today as a {ranking.ranking}</h1>;
}

export default RatingToday;
