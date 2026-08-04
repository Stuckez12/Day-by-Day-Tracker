"use client";

import { Temporal } from "@js-temporal/polyfill";

import { DayMonthStringValues } from "@/lib/interfaces/datetime";

export const dateTimeFormatter = new Intl.DateTimeFormat("en", {
  weekday: "long",
  month: "long",
});

export function getDateValues(date: string): DayMonthStringValues {
  const plainDate = Temporal.PlainDate.from(date);
  const formattedDate = dateTimeFormatter.format(
    new Date(`${plainDate.toString()}T00:00:00`),
  );

  const stringValues = formattedDate.split(" ");
  const numberValues = date.split("-");
  const dayPositions = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
  ];

  return {
    day: stringValues[1],
    dayPos: dayPositions.indexOf(stringValues[1]) + 1,
    month: stringValues[0],
    dayNum: Number(numberValues[2]),
    monthNum: Number(numberValues[1]),
    year: Number(numberValues[0]),
  };
}

export function getDayCountForMonth(date: string): number {
  return Temporal.PlainDate.from(date).daysInMonth;
}

export function getDateTextForDay(date: string): string {
  const dateData = getDateValues(date);

  return `${dateData.dayNum} ${dateData.month} ${dateData.year}`;
}
