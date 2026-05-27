import { useContext, useEffect, useState } from "react";
import { Temporal } from "@js-temporal/polyfill";

import type { RankingProps, RankingTextBoxProps } from "interfaces/ranking";

import APICall from "scripts/api.ts";
import { ContextLanding } from "contexts/ContextLanding";

function TextInputs() {
  const { refreshRankingLanding, setRefreshRankingLanding } =
    useContext(ContextLanding);

  const [form, setForm] = useState<RankingTextBoxProps>({
    text_events: refreshRankingLanding.text_events,
    text_notes: refreshRankingLanding.text_notes,
  });

  function handleChange(e: React.ChangeEvent<HTMLTextAreaElement>) {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });

    console.log(form);
  }

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setForm({
      text_events: refreshRankingLanding.text_events || "",
      text_notes: refreshRankingLanding.text_notes || "",
    });
  }, [refreshRankingLanding, setRefreshRankingLanding]);

  function onSubmit(e: React.MouseEvent<HTMLButtonElement>) {
    e.preventDefault();

    async function save_text_data(form: RankingTextBoxProps) {
      const [success, data] = await APICall.put<RankingProps>(
        "/ranking/rank/notes",
        {
          day: Temporal.Now.plainDateISO().toString(),
          text_events: form.text_events,
          text_notes: form.text_notes,
        },
      );

      if (success) {
        setRefreshRankingLanding(data!);
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
