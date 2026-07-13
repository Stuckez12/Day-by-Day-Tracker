import clsx from "clsx";
import { useContext } from "react";

import { rankTodayNumberQuery } from "@/lib/queries/ranking";
import { RankingTrackerContext } from "@/components/tracker/rateDayContext";

import "@/styles/tracker/ranking.scss";

interface RateDayButtonProps {
  ranking: number;
  current_rank?: number;
}

export default function RateDayButton({
  ranking,
  current_rank,
}: RateDayButtonProps) {
  const { setRefreshRanking } = useContext(RankingTrackerContext);

  async function rate_today() {
    const result = await rankTodayNumberQuery({ ranking });

    if (result.ok) {
      console.log("Success");
      setRefreshRanking(result.data);
    } else {
      console.log("Error");
      console.log(result.error);
    }
  }

  return (
    <div
      className={clsx("rate-button", {
        "is-selected": ranking == current_rank,
      })}
      onClick={rate_today}
    >
      <p className="rate-text">{ranking}</p>
    </div>
  );
}
