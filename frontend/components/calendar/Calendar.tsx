"use client";

import { useEffect, useRef, useState } from "react";
import GridItem from "@/components/layouts/grid/GridItem";
import GridRow from "@/components/layouts/grid/GridRow";
import { getDateValues, getDayCountForMonth } from "@/lib/common/datetime";
import { getRankingRangeQuery } from "@/lib/queries/ranking";
import { RankingProp } from "@/lib/interfaces/ranking";
import CalendarItem from "@/components/calendar/CalendarItem";
import { CalendarItemData } from "@/lib/interfaces/calendar";

export default function Calendar() {
  const calendarRef = useRef<HTMLDivElement>(null);
  const [calendarWidth, setCalendarWidth] = useState(0);
  const [calendarDatesData, setCalendarDatesData] = useState<
    CalendarItemData[][]
  >([]);

  const weekdayCount = 7;

  // Set the calendar width
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

  // Set the calendar width
  useEffect(() => {
    function setCalendarDatesWData(
      data: RankingProp[],
      startDate: string,
      rowCount: number,
    ) {
      let currentDate = Temporal.PlainDate.from(startDate);
      let calendarData = [];

      data.reverse();

      for (let row = 0; row < rowCount; row++) {
        let rowData = [];

        for (let item = 0; item < weekdayCount; item++) {
          const checkingDate = currentDate;
          currentDate = currentDate.add({ days: 1 });

          if (data.length <= 0) {
            rowData.push({ data: null, date: checkingDate.toString() });
            continue;
          }

          if (data[0].day == checkingDate.toString()) {
            rowData.push({ data: data[0], date: checkingDate.toString() });
            data.shift();
          } else {
            console.log(
              `Earliest: ${data[0].day}. Not found ${checkingDate.toString()}.`,
            );
            rowData.push({ data: null, date: checkingDate.toString() });
          }
        }

        calendarData.push(rowData);
      }

      setCalendarDatesData(calendarData);
      console.log(calendarData);
    }

    async function setCalendarData() {
      const monthSelected = Temporal.PlainDate.from("2026-07-01");

      const monthFirstDayData = getDateValues(monthSelected.toString());
      const monthDayCount = getDayCountForMonth(monthSelected.toString());

      const dayOffset = monthFirstDayData.dayPos - 1;
      const calendarDayRows = Math.ceil(
        (monthDayCount + dayOffset) / weekdayCount,
      );
      const extraDayCount =
        weekdayCount - Math.ceil((monthDayCount + dayOffset) % weekdayCount);

      const start_date = monthSelected.subtract({ days: dayOffset });
      const end_date = monthSelected.add({
        days: monthDayCount + extraDayCount - 1,
      });

      const result = await getRankingRangeQuery(
        start_date.toString(),
        end_date.toString(),
      );

      if (result.ok) {
        setCalendarDatesWData(
          result.data,
          start_date.toString(),
          calendarDayRows,
        );
      } else {
        console.log("Error when getting calendar data");
        console.log(result.error);
      }
    }

    setCalendarData();
  }, []);

  const weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
  const calendarItemSize = 40;
  const calendarDates = [
    // Temp
    [1, 2, 3, 4, 5, 6, 7],
    [1, 2, 3, 4, 5, 6, 7],
    [1, 2, 3, 4, 5, 6, 7],
    [1, 2, 3, 4, 5, 6, 7],
    [1, 2, 3, 4, 5, 6, 7],
  ];

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
        {/* // replace with calendarDatesData once completed */}
        {calendarDatesData.map((row, i) => (
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
                <CalendarItem data={item.data} date={item.date} />
              </GridItem>
            ))}
          </GridRow>
        ))}
      </div>
    </div>
  );
}
