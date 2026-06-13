"use client";

import { useEffect, useState } from "react";

import RankRow from "@/components/ranking/RankRow";
import { RankingProp } from "@/lib/interfaces/ranking";
import { getAllRanksQuery } from "@/lib/queries/ranking";

import "@/styles/common/tables.scss";

interface RankTableProps {}

export default function RankTable({}: RankTableProps) {
  const [allRanks, setAllRanks] = useState<RankingProp[]>();

  useEffect(() => {
    async function get_all_ranks() {
      const result = await getAllRanksQuery();

      if (result.isOk()) {
        setAllRanks(result.value);
      } else {
        console.log("Error when getting data");
        console.log(result.error);
      }
    }
    get_all_ranks();
  }, []);

  return (
    <table>
      <thead>
        <tr className="table-row table-header-row">
          <th>Date</th>
          <th>Ranking</th>
          <th>Has Text</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        {allRanks &&
          allRanks.map((rank) => <RankRow key={rank.id} rank={rank} />)}
      </tbody>
    </table>
  );
}
