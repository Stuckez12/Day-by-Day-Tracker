"use client";

import { Temporal } from "@js-temporal/polyfill";

import Calendar from "@/components/calendar/Calendar";
import { CalendarContext } from "@/components/calendar/CalendarContext";
import SubmitButton from "@/components/common/form-inputs/SubmitButton";
import TextAreaInput from "@/components/common/form-inputs/TextAreaInput";
import { getDateTextForDay } from "@/lib/common/datetime";
import { updateForm } from "@/lib/common/updateForm";
import { getRankQuery, rankDayQuery } from "@/lib/queries/ranking";
import { useContext, useEffect, useState } from "react";
import ListErrors from "@/components/common/errors/ListErrors";

export default function EditCalendarDataForm() {
  const [errors, setErrors] = useState<string[]>([]);
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

  async function submitForm(e: React.SubmitEvent<HTMLFormElement>) {
    e.preventDefault();

    console.log("Form data:", ranking);

    const result = await rankDayQuery(ranking);

    if (result.ok) {
      console.log("Info Updated Successfully");

      setErrors([]);
      setRanking(result.data);

      return;
    }

    const all_errors = result.error.errors;
    let display_errors: string[] = [];

    if (result.error.api_response) {
      display_errors = [`${all_errors.api}`];
    } else {
      display_errors = display_errors.concat(all_errors.email);
    }

    setErrors(display_errors);
  }

  function onChange(
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
  ) {
    return updateForm(e, ranking, setRanking);
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-[60%_40%] md:gap-x-4">
      <Calendar />
      <form onSubmit={submitForm}>
        <h1>{getDateTextForDay(ranking.day)}</h1>
        <TextAreaInput
          name="ranking"
          value={ranking.ranking?.toString()}
          onChange={onChange}
          placeholder="Rank today between 0 - 10"
        />
        <TextAreaInput
          name="text_events"
          value={ranking.text_events}
          onChange={onChange}
          placeholder="Insert any events that happened today..."
        />
        <TextAreaInput
          name="text_notes"
          value={ranking.text_notes}
          onChange={onChange}
          placeholder="Insert anything notable that happened today..."
        />
        <ListErrors errors={errors} />
        <SubmitButton label="Submit" />
      </form>
    </div>
  );
}
