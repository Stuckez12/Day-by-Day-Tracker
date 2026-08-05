"use client";

import Calendar from "@/components/calendar/Calendar";
import ListErrors from "@/components/common/errors/ListErrors";
import SubmitButton from "@/components/common/form-inputs/SubmitButton";
import TextAreaInput from "@/components/common/form-inputs/TextAreaInput";
import PageWrapper from "@/components/common/PageWrapper";
import { getDateTextForDay } from "@/lib/common/datetime";
import { updateForm } from "@/lib/common/updateForm";
import { RankingUIDataProp } from "@/lib/interfaces/ranking";
import { getRankQuery } from "@/lib/queries/ranking";
import { useEffect, useState } from "react";

export default function RankingPage() {
  const [errors, setErrors] = useState<string[]>([]);
  const [form, setForm] = useState<RankingUIDataProp>({
    day: Temporal.Now.plainDateISO().toString(),
    ranking: undefined,
    text_events: "",
    text_notes: "",
  });

  useEffect(() => {
    async function getRank() {
      const response = await getRankQuery(
        Temporal.Now.plainDateISO().toString(),
      );

      if (response.ok) {
        setForm(response.data);
      } else {
        console.log("Error occured");
      }
    }

    getRank();
  }, []);

  function onChange(
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
  ) {
    return updateForm(e, form, setForm);
  }

  return (
    <PageWrapper>
      <div className="grid grid-cols-1 md:grid-cols-[60%_40%] md:gap-x-4">
        <Calendar />
        <form>
          <h1>{getDateTextForDay(form.day)}</h1>
          <TextAreaInput
            name="ranking"
            value={form.ranking?.toString()}
            onChange={onChange}
          />
          <TextAreaInput
            name="text_events"
            value={form.text_events}
            onChange={onChange}
          />
          <TextAreaInput
            name="text_notes"
            value={form.text_notes}
            onChange={onChange}
          />
          <ListErrors errors={errors} />
          <SubmitButton label="Submit" />
        </form>
      </div>
    </PageWrapper>
  );
}
