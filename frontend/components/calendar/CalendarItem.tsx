"use client";

import { getDateValues } from "@/lib/common/datetime";
import { CalendarItemData } from "@/lib/interfaces/calendar";

export default function CalendarItem({ data, date }: CalendarItemData) {
  const dayData = getDateValues(date);

  // Worst to best
  const rankingColourRange = [
    "#f01d1d",
    "#F44336",
    "#FF7A00",
    "#f2c231",
    "#f0db4c",
    "#b6e269",
    "#6ad26d",
    "#22C55E",
    "#16A34A",
    "#15803D",
    "#166534",
  ];

  let calendarBGColor = "#d9d9d9";

  if (data !== null) {
    if (data.ranking != null) {
      calendarBGColor = rankingColourRange[data.ranking];
    }
  }

  return (
    <div
      className="w-full h-full flex items-center"
      style={{ backgroundColor: calendarBGColor }}
    >
      <p className="m-0 text-center w-full">{dayData.dayNum}</p>
    </div>
  );
}
