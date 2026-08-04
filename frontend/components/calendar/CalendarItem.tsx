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
    <div className="w-full h-full flex p-[4]">
      <div
        className="w-full h-full flex items-center rounded-md hover:border-2 hover:border-[#afafaf] active:border-2 active:border-[#9f9f9f]"
        style={{ backgroundColor: calendarBGColor }}
      >
        <span className="text-center w-full font-bold text-black">
          {dayData.dayNum}
        </span>
      </div>
    </div>
  );
}
