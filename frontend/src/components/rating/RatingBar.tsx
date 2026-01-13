import React from "react";
import { useEffect, useState } from "react";
import { Temporal } from "@js-temporal/polyfill";

import RateValueButton from "components/rating/RatingValueButton";
import RatingToday from "components/rating/RatingToday";

import type { RankingProps } from "interfaces/ranking";

import APICall from "scripts/api.ts";

import "styles/rating/rating_button.scss";

interface DayRanking {
  id: string;
  personal_id: string;
  day: Date;
  ranking: number;
  created_at: Date;
  updated_at: Date;
}

function RatingBar() {
  const [rank_today, setRank] = useState<RankingProps>();
  const [rerendering, setRenderState] = useState(false);
  const [initialise, initialiseComponent] = useState(false);

  useEffect(() => {
    if (!rerendering) return;

    async function fetchRank() {
      const [success, response, message] = await APICall.get<RankingProps>(
        "/ranking/today"
      );

      if (success) {
        setRank(response!);
      } else {
        console.log("Error when getting data");
        console.log(message);
      }
    }
    fetchRank();
    setRenderState(false);
  }, [initialise, rerendering]);

  const detect_click = async (e: React.MouseEvent<HTMLDivElement>) => {
    const target = e.target;
    if (!target) return;

    const clickedDiv = (target as HTMLElement).closest("div");
    if (!clickedDiv) return;

    if (!clickedDiv || clickedDiv === e.currentTarget) {
      const parentDiv = (clickedDiv as HTMLElement).parentElement?.closest(
        "div"
      );

      if (!parentDiv) return;
    }

    console.log("Clicked button:", clickedDiv.textContent);

    const [success, response, err_message] = await APICall.put<DayRanking>(
      "/ranking/rank",
      {
        day: Temporal.Now.plainDateISO().toString(),
        ranking: Number(clickedDiv.textContent),
      }
    );

    console.log(success, response, err_message);

    setRenderState(success);
  };

  let ranking = rank_today ? rank_today.ranking : null;

  if (!initialise) {
    setRenderState(true);
    initialiseComponent(true);
  }

  return (
    <>
      <RatingToday ranking={ranking} />
      <div
        className="rating-button-bar"
        onClick={detect_click}
        style={{ display: "flex" }}
      >
        <RateValueButton value="0" selected={ranking} />
        <RateValueButton value="1" selected={ranking} />
        <RateValueButton value="2" selected={ranking} />
        <RateValueButton value="3" selected={ranking} />
        <RateValueButton value="4" selected={ranking} />
        <RateValueButton value="5" selected={ranking} />
        <RateValueButton value="6" selected={ranking} />
        <RateValueButton value="7" selected={ranking} />
        <RateValueButton value="8" selected={ranking} />
        <RateValueButton value="9" selected={ranking} />
        <RateValueButton value="10" selected={ranking} />
      </div>
    </>
  );
}

export default RatingBar;
