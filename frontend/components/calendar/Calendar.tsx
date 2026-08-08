"use client";

import { Temporal } from "@js-temporal/polyfill";

import { useEffect, useRef, useState } from "react";
import GridItem from "@/components/layouts/grid/GridItem";
import GridRow from "@/components/layouts/grid/GridRow";
import { getDateValues, getDayCountForMonth } from "@/lib/common/datetime";
import { getRankingRangeQuery } from "@/lib/queries/ranking";
import { RankingProp } from "@/lib/interfaces/ranking";
import CalendarItem from "@/components/calendar/CalendarItem";
import { CalendarItemData } from "@/lib/interfaces/calendar";
import CalendarHeader from "./CalendarHeader";
import Button from "@/components/common/buttons/Button";
import Icon from "@/components/common/Icon";
export default function Calendar() {
  const calendarRef = useRef<HTMLDivElement>(null);
  const [calendarWidth, setCalendarWidth] = useState(0);
  const [calendarDatesData, setCalendarDatesData] = useState<
    CalendarItemData[][]
  >([]);

  const [currentDate, setCurrentDate] = useState(
    Temporal.Now.plainDateISO().with({ day: 1 }),
  );

  const weekdayCount = 7;

  function changeMonthSelected(monthModifier: number) {
    console.log(currentDate.toString());
    setCurrentDate((prev) =>
      prev.add({
        months: monthModifier,
      }),
    );

    console.log(currentDate.toString());
  }

  function resetMonthToCurrent() {
    setCurrentDate(Temporal.Now.plainDateISO().with({ day: 1 }));
  }

  // Get calendar width
  useEffect(() => {
    const element = calendarRef.current;
    if (!element) return;

    const observer = new ResizeObserver(([entry]) => {
      setCalendarWidth(entry.contentRect.width);
    });

    observer.observe(element);

    return () => observer.disconnect();
  }, []);

  // Set calendar data
  useEffect(() => {
    function setCalendarDatesWData(
      data: RankingProp[],
      startDate: string,
      rowCount: number,
    ) {
      let currentDateTemp = Temporal.PlainDate.from(startDate);
      const calendarData = [];

      data.reverse();

      for (let row = 0; row < rowCount; row++) {
        const rowData = [];

        for (let item = 0; item < weekdayCount; item++) {
          const checkingDate = currentDateTemp;
          currentDateTemp = currentDateTemp.add({ days: 1 });

          if (data.length <= 0) {
            rowData.push({ data: null, date: checkingDate.toString() });
            continue;
          }

          if (data[0].day == checkingDate.toString()) {
            rowData.push({ data: data[0], date: checkingDate.toString() });
            data.shift();
          } else {
            rowData.push({ data: null, date: checkingDate.toString() });
          }
        }

        calendarData.push(rowData);
      }

      setCalendarDatesData(calendarData);
    }

    async function setCalendarData() {
      const monthSelected = currentDate;

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
  }, [currentDate]);

  const weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
  const calendarItemSize = calendarWidth / weekdayCount;

  const displayData = getDateValues(currentDate.toString());
  const monthDisplay = `${displayData.month} ${displayData.year}`;

  return (
    <div className="w-full flex flex-column gap-y-2" ref={calendarRef}>
      <div className="flex gap-x-2" style={{ width: calendarItemSize * 7 }}>
        <Button
          style="secondary"
          size="square"
          onClick={() => changeMonthSelected(-1)}
        >
          <Icon svgPath="/arrows/arrow-back-rounded.svg" alt="Back Arrow" />
        </Button>
        <Button style="secondary" size="sharp" onClick={resetMonthToCurrent}>
          {monthDisplay}
        </Button>
        <Button
          style="secondary"
          size="square"
          onClick={() => changeMonthSelected(1)}
        >
          <Icon
            svgPath="/arrows/arrow-forward-rounded.svg"
            alt="Forward Arrow"
          />
        </Button>
      </div>
      <div className="flex flex-column">
        <GridRow
          width={calendarItemSize * 7}
          height={calendarItemSize / 2}
          key={"Calendar Index"}
          classes="rounded-md bg-[#d9d9d9]"
          styles={{ margin: "4px" }}
        >
          {weekdays.map((day, _) => (
            <GridItem
              width={calendarItemSize}
              height={calendarItemSize / 2}
              key={day}
            >
              <CalendarHeader header={day} />
            </GridItem>
          ))}
        </GridRow>
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
