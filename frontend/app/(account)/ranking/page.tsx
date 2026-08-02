"use client";

import Calendar from "@/components/calendar/Calendar";
import ListErrors from "@/components/common/errors/ListErrors";
import SubmitButton from "@/components/common/form-inputs/SubmitButton";
import TextAreaInput from "@/components/common/form-inputs/TextAreaInput";
import PageWrapper from "@/components/common/PageWrapper";
import { updateForm } from "@/lib/common/updateForm";
import { RankingUIDataProp } from "@/lib/interfaces/ranking";
import { useState } from "react";

export default function RankingPage() {
  const [errors, setErrors] = useState<string[]>([]);
  const [form, setForm] = useState<RankingUIDataProp>({
    day: "",
    ranking: undefined,
    text_events: "",
    text_notes: "",
  });

  function onChange(
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
  ) {
    return updateForm(e, form, setForm);
  }

  return (
    <PageWrapper>
      <div className="grid grid-cols-1 md:grid-cols-[60%_40%]">
        <Calendar />
        <form>
          <h1>{form.day}</h1>
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
