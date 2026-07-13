"use client";

import { useContext, useEffect, useState } from "react";

import ListErrors from "@/components/common/errors/ListErrors";
import TextAreaInput from "@/components/common/form-inputs/TextAreaInput";
import SubmitButton from "@/components/common/form-inputs/SubmitButton";
import { RankingTrackerContext } from "@/components/tracker/rateDayContext";
import { updateForm } from "@/lib/common/updateForm";
import { RankingTextDataProp } from "@/lib/interfaces/ranking";
import { rankTodayNotesQuery } from "@/lib/queries/ranking";

// interface RateDayTextProps {}

export default function RateDayText() {
  const [errors, setErrors] = useState<string[]>([]);
  const { refreshRanking } = useContext(RankingTrackerContext);
  const [form, setForm] = useState<RankingTextDataProp>({
    text_events: "",
    text_notes: "",
  });

  function onChange(e: React.ChangeEvent<HTMLTextAreaElement>) {
    return updateForm(e, form, setForm);
  }

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setForm(refreshRanking as RankingTextDataProp);
  }, [refreshRanking]);

  async function submitForm(e: React.SubmitEvent<HTMLFormElement>) {
    e.preventDefault();

    console.log("Form data:", form);

    const result = await rankTodayNotesQuery(form);

    if (result.ok) {
      setForm(result.data);

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

  return (
    <form onSubmit={submitForm}>
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
  );
}
