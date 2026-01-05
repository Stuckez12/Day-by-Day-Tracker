import React from "react";

import RateValueButton from "components/rating/RatingValueButton";
import APICall from "scripts/api.ts";

interface DayRanking {
  ranking: number;
  day: Date;
  created_at: Date;
  id: string;
  personal_id: string;
  updated_at: Date;
}

function RatingBar() {
  const detect_click = async (e: React.MouseEvent<HTMLDivElement>) => {
    const target = e.target;
    if (!target) return;

    const clicked = (target as HTMLElement).closest("p");
    if (!clicked) return;

    console.log("Clicked button:", clicked.textContent);

    const [success, response, err_message] = await APICall.put<DayRanking>(
      "/ranking/rank",
      {
        day: "2026-01-05",
        ranking: Number(clicked.textContent),
      }
    );

    console.log(success, response, err_message);
  };

  return (
    <div onClick={detect_click}>
      <RateValueButton value="0" />
      <RateValueButton value="1" />
      <RateValueButton value="2" />
      <RateValueButton value="3" />
      <RateValueButton value="4" />
      <RateValueButton value="5" />
      <RateValueButton value="6" />
      <RateValueButton value="7" />
      <RateValueButton value="8" />
      <RateValueButton value="9" />
      <RateValueButton value="10" />
    </div>
  );
}

export default RatingBar;
