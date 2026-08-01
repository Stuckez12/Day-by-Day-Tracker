"use client";

import { useEffect, useRef, useState } from "react";
import GridItem from "@/components/layouts/grid/GridItem";
import GridRow from "@/components/layouts/grid/GridRow";
import { getDateValues, getDayCountForMonth } from "@/lib/common/datetime";

export default function Calendar() {
  const calendarRef = useRef<HTMLDivElement>(null);
  const [calendarWidth, setCalendarWidth] = useState(0);

  useEffect(() => {
    if (!calendarRef.current) return;

    const observer = new ResizeObserver(([entry]) => {
      setCalendarWidth(entry.contentRect.width);
    });

    observer.observe(calendarRef.current);

    return () => {
      observer.disconnect();
    };
  }, []);

  // Month selection

  const monthFirstDayData = getDateValues("2026-08-01");
  const monthDayCount = getDayCountForMonth("2026-08-01");
  const prevMonthDayCount = getDayCountForMonth("2026-07-01");

  const calendarDayRows = Math.ceil(
    (monthDayCount + (monthFirstDayData.dayPos - 1)) / 7,
  );

  const prevMonthDayDisplayCount = monthFirstDayData.dayPos - 1;

  const weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
  const calendarItemSize = 40;

  // Date position calculation

  const calendarDates = [
    [1, 2, 3, 4, 5, 6, 7],
    [1, 2, 3, 4, 5, 6, 7],
    [1, 2, 3, 4, 5, 6, 7],
    [1, 2, 3, 4, 5, 6, 7],
    [1, 2, 3, 4, 5, 6, 7],
  ];

  console.log(monthFirstDayData);
  console.log(monthDayCount);

  return (
    <div className="w-auto bg-white height-48">
      <div className="">
        <p>August</p>
      </div>
      <div className="flex flex-column">
        <GridRow
          width={calendarItemSize * 7}
          height={calendarItemSize}
          key={"Calendar Index"}
        >
          {weekdays.map((day, i) => (
            <GridItem
              width={calendarItemSize}
              height={calendarItemSize}
              key={day}
            >
              <span>{day}</span>
            </GridItem>
          ))}
        </GridRow>
        {calendarDates.map((row, i) => (
          <GridRow
            width={calendarItemSize * 7}
            height={calendarItemSize}
            key={i}
          >
            {row.map((item, j) => (
              <GridItem
                width={calendarItemSize}
                height={calendarItemSize}
                key={j + i * 7}
              >
                <span>{item}</span>
              </GridItem>
            ))}
          </GridRow>
        ))}
      </div>
    </div>
  );
}
