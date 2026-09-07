import clsx from "clsx";
import { useContext } from "react";

import { rankTodayNumberQuery } from "@/lib/queries/ranking";
import { RankingTrackerContext } from "@/components/tracker/rateDayContext";

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
      className={clsx(
        "m-1 flex size-16 cursor-pointer items-center justify-center rounded-lg bg-[#007ea7] hover:bg-[#00a8e8] active:bg-[#00a8e8]",
        {
          "bg-[#00a8e8]": ranking == current_rank,
        },
      )}
      onClick={rate_today}
    >
      <p className="m-0 text-center text-2xl text-white">{ranking}</p>
    </div>
  );
}
