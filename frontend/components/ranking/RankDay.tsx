import { useState } from "react";

import ListErrors from "@/components/common/errors/ListErrors";
import SubmitButton from "@/components/common/form-inputs/SubmitButton";
import TextAreaInput from "@/components/common/form-inputs/TextAreaInput";
import TextInput from "@/components/common/form-inputs/TextInput";
import { updateForm } from "@/lib/common/updateForm";
import { RankingUIDataProp } from "@/lib/interfaces/ranking";
import { rankDayQuery } from "@/lib/queries/ranking";

function RankDay() {
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

  async function submitForm(e: React.MouseEvent<HTMLButtonElement>) {
    e.preventDefault();

    console.log("Form data:", form);

    const result = await rankDayQuery(form);

    if (result.isOk()) {
      setForm(result.value);
      setErrors([]);
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

  let ranking = "";

  if (form.ranking != undefined) {
    ranking = form.ranking.toString();
  }

  return (
    <div>
      <TextInput name="day" label="Day" value={form.day} onChange={onChange} />
      <TextInput
        name="ranking"
        label="Ranking"
        value={ranking}
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
      <SubmitButton label="Submit" onSubmit={submitForm} />
    </div>
  );
}

export default RankDay;
