import { useContext, useEffect, useState } from "react";

import { ContextRefreshList } from "contexts/ContextRefreshList";

import RatingRow from "components/rating/RatingRow.tsx";

import type { RankingProps } from "interfaces/ranking";

import APICall from "scripts/api.ts";

import "styles/common/tables.scss";

function RatingList() {
  const [rankings, setRankings] = useState<RankingProps[]>([]);

  const { refreshList, setRefreshList } = useContext(ContextRefreshList);

  useEffect(() => {
    if (!refreshList) {
      return;
    }

    const fetchRankings = async () => {
      const [success, data, _] =
        await APICall.get<RankingProps[]>("/ranking/all");

      if (success) {
        setRankings(data!);
      }
    };

    fetchRankings();
    setRefreshList(false);
  }, [refreshList]);

  return (
    <div className="table-base">
      <table>
        <tr className="table-row table-header-row">
          <th>Day</th>
          <th>Ranking</th>
        </tr>
        {rankings.map(({ day, ranking }) => (
          <RatingRow day={day} ranking={ranking} />
        ))}
      </table>
    </div>
  );
}

export default RatingList;
