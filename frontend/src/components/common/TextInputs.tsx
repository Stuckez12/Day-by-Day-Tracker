import { useEffect, useState } from "react";
import { Temporal } from "@js-temporal/polyfill";

import type { RankingProps, RankingTextBoxProps } from "interfaces/ranking";

import APICall from "scripts/api.ts";

function TextInputs() {
  const [form, setForm] = useState<RankingTextBoxProps>({
    text_events: "",
    text_notes: "",
  });

  function handleChange(e: React.ChangeEvent<HTMLTextAreaElement>) {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });

    console.log(form);
  }

  useEffect(() => {
    async function fetchRank() {
      const [success, response, message] =
        await APICall.get<RankingProps>("/ranking/today");

      if (success) {
        setForm(response!);
      } else {
        console.log("Error when getting data");
        console.log(message);
      }
    }
    fetchRank();
  }, []);

  function onSubmit(e: React.MouseEvent<HTMLButtonElement>) {
    e.preventDefault();

    console.log("Form data:", form);

    async function save_text_data(form: RankingTextBoxProps) {
      const [success] = await APICall.put<RankingProps>("/ranking/rank/notes", {
        day: Temporal.Now.plainDateISO().toString(),
        text_events: form.text_events,
        text_notes: form.text_notes,
      });

      if (success) {
        console.log("Success. Now redirect");
      } else {
        console.log("Error when submitting text");
      }
    }

    save_text_data(form);
  }

  return (
    <div>
      <div className="textarea-input">
        <textarea
          name="text_events"
          value={form.text_events}
          onChange={handleChange}
          placeholder="Insert any event that happened today..."
          autoComplete="new-field"
        />
      </div>

      <div className="textarea-input">
        <textarea
          name="text_notes"
          value={form.text_notes}
          onChange={handleChange}
          placeholder="Insert anything notable that happened today..."
          autoComplete="new-field"
        />
      </div>
      <button className="submit-button" onClick={onSubmit}>
        Submit
      </button>
    </div>
  );
}

export default TextInputs;
