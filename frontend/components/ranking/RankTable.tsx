"use client";

import { useEffect, useState } from "react";

import RankRow from "@/components/ranking/RankRow";
import { RankingProp } from "@/lib/interfaces/ranking";
import { getAllRanksQuery } from "@/lib/queries/ranking";

// interface RankTableProps {}

export default function RankTable() {
  const [allRanks, setAllRanks] = useState<RankingProp[]>();

  useEffect(() => {
    async function get_all_ranks() {
      const result = await getAllRanksQuery();

      if (result.ok) {
        setAllRanks(result.data);
      } else {
        console.log("Error when getting data");
        console.log(result.error);
      }
    }
    get_all_ranks();
  }, []);

  return (
    <table className="w-full border-collapse pt-8">
      <thead>
        <tr className="bg-[#007ea7] text-left text-white [&>th]:border [&>th]:border-[#ddd] [&>th]:p-2 [&>th]:py-3">
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
