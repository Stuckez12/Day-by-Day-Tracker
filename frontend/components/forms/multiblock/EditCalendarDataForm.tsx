"use client";

import Calendar from "@/components/calendar/Calendar";
import { CalendarContext } from "@/components/calendar/CalendarContext";
import SubmitButton from "@/components/common/form-inputs/SubmitButton";
import TextAreaInput from "@/components/common/form-inputs/TextAreaInput";
import { getDateTextForDay } from "@/lib/common/datetime";
import { updateForm } from "@/lib/common/updateForm";
import { getRankQuery } from "@/lib/queries/ranking";
import { useContext, useEffect } from "react";

export default function EditCalendarDataForm() {
  const { ranking, setRanking } = useContext(CalendarContext);

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

  function onChange(
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
  ) {
    return updateForm(e, ranking, setRanking);
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-[60%_40%] md:gap-x-4">
      <Calendar />
      <form>
        <h1>{getDateTextForDay(ranking.day)}</h1>
        <TextAreaInput
          name="ranking"
          value={ranking.ranking?.toString()}
          onChange={onChange}
        />
        <TextAreaInput
          name="text_events"
          value={ranking.text_events}
          onChange={onChange}
        />
        <TextAreaInput
          name="text_notes"
          value={ranking.text_notes}
          onChange={onChange}
        />
        {/* <ListErrors errors={errors} /> */}
        <SubmitButton label="Submit" />
      </form>
    </div>
  );
}
