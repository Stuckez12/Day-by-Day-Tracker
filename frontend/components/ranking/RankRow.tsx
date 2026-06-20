import { RankingProp } from "@/lib/interfaces/ranking";

function RatingRow({ rank }: { rank: RankingProp }) {
  const has_text =
    rank.text_events !== undefined || rank.text_notes !== undefined;

  return (
    <tr className="table-row table-data-row">
      <td>{rank.day}</td>
      <td>{rank.ranking}</td>
      <td>{has_text}</td>
      <td>
        <button>Edit</button>
      </td>
    </tr>
  );
}

export default RatingRow;
