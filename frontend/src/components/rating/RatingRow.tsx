import type { RankingRowProps } from "interfaces/ranking";

import "styles/common/tables.scss";

function RatingRow({ day, ranking }: RankingRowProps) {
  return (
    <tr className="table-row table-data-row">
      <td>{day}</td>
      <td>{ranking}</td>
    </tr>
  );
}

export default RatingRow;
