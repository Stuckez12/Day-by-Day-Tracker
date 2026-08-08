"use client";

import { Temporal } from "@js-temporal/polyfill";

import { CalendarContext } from "@/components/calendar/CalendarContext";
import { RankingUIDataProp } from "@/lib/interfaces/ranking";
import { getRankQuery } from "@/lib/queries/ranking";
import { PropsWithChildren, useEffect, useState } from "react";

export default function CalendarProvider({ children }: PropsWithChildren) {
  const [ranking, setRanking] = useState<RankingUIDataProp>({
    day: "",
    ranking: undefined,
    text_events: undefined,
    text_notes: undefined,
  });

  useEffect(() => {
    async function getRank() {
      const response = await getRankQuery(
        Temporal.Now.plainDateISO().toString(),
      );

      if (response.ok) {
        console.log("Setting rank");
        console.log(response.data);
        setRanking(response.data);
      } else {
        console.log("Error occured");
        console.log(response.error);
      }
    }

    getRank();
  }, []);

  return (
    <CalendarContext.Provider value={{ ranking, setRanking }}>
      {children}
    </CalendarContext.Provider>
  );
}
