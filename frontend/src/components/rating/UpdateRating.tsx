import { useContext, useState } from "react";

import { ContextRefreshList } from "contexts/ContextRefreshList";

import type { RankingProps, RankingRowProps } from "interfaces/ranking";

import APICall from "scripts/api.ts";

import "styles/common/form-inputs.scss";
import "styles/common/tables.scss";

function UpdateRating() {
  const [form, setForm] = useState<RankingRowProps>({
    day: "",
    ranking: 0,
  });

  const { setRefreshList } = useContext(ContextRefreshList);

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const { name, value } = e.target;
    setForm({
      ...form,
      [name]: value,
    });
  }

  function onSubmit(e: React.MouseEvent<HTMLButtonElement>) {
    e.preventDefault();

    console.log("Form data:", form);

    async function update_ranking(form: RankingRowProps) {
      const [success, _, message] = await APICall.put<RankingProps>(
        "/ranking/rank",
        {
          day: form.day,
          ranking: Number(form.ranking),
        },
      );

      if (success) {
        console.log("Success. Now refresh");
        setRefreshList(true);
      } else {
        console.log("Error when getting data");
        console.log(message);
      }
    }

    update_ranking(form);
  }

  return (
    <form>
      <h1 className="form-title">Rank Specific Day</h1>
      <div className="text-input">
        <input
          type="text"
          name="day"
          value={form.day}
          onChange={handleChange}
          placeholder=""
          autoComplete="new-field"
        />
        <label>Day</label>
      </div>

      <div className="text-input">
        <input
          type="text"
          name="ranking"
          value={form.ranking!}
          onChange={handleChange}
          placeholder=""
          autoComplete="new-field"
        />
        <label>Ranking</label>
      </div>
      <button className="submit-button" onClick={onSubmit}>
        Submit
      </button>
    </form>
  );
}

export default UpdateRating;
