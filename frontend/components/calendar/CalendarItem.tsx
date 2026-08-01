"use client";

import { getDateValues } from "@/lib/common/datetime";
import { CalendarItemData } from "@/lib/interfaces/calendar";

export default function CalendarItem({ data, date }: CalendarItemData) {
  const dayData = getDateValues(date);

  return (
    <div className="w-auto h-auto">
      <p>{dayData.dayNum}</p>
    </div>
  );
}
