"use client";

import { getDateValues } from "@/lib/common/datetime";
import { CalendarItemData } from "@/lib/interfaces/calendar";
import { CalendarContext } from "@/components/calendar/CalendarContext";
import { useContext } from "react";
import { getRankQuery } from "@/lib/queries/ranking";

export default function CalendarItem({ data, date }: CalendarItemData) {
  const dayData = getDateValues(date);

  const { setRanking } = useContext(CalendarContext);

  async function selectDay() {
    const response = await getRankQuery(date);

    if (response.ok) {
      setRanking(response.data);
    } else {
      console.log("Error fetching data");
      console.log(response.error);
    }
  }

  // Worst to best
  const rankingColourRange = [
    "bg-rank-0",
    "bg-rank-1",
    "bg-rank-2",
    "bg-rank-3",
    "bg-rank-4",
    "bg-rank-5",
    "bg-rank-6",
    "bg-rank-7",
    "bg-rank-8",
    "bg-rank-9",
    "bg-rank-10",
  ];

  let calendarBGColor = "bg-calendar-empty";

  if (data !== null) {
    if (data.ranking != null) {
      calendarBGColor = rankingColourRange[data.ranking];
    }
  }

  return (
    <div className="w-full h-full flex p-[4]">
      <div
        className={`w-full h-full flex items-center rounded-md hover:border-2 hover:border-calendar-border-hover active:border-2 active:border-calendar-border-clicked ${calendarBGColor}`}
        onClick={selectDay}
      >
        <span className="text-center w-full font-bold text-default-text-color">
          {dayData.dayNum}
        </span>
      </div>
    </div>
  );
}
