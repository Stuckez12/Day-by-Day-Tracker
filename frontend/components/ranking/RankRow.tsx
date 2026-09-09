import { RankingProp } from "@/lib/interfaces/ranking";

function RatingRow({ rank }: { rank: RankingProp }) {
  const has_text =
    rank.text_events !== undefined || rank.text_notes !== undefined;

  return (
    <tr className="odd:bg-table-row-color-odd even:bg-table-row-color-even hover:bg-table-row-color-highlight [&>td]:border [&>td]:border-table-border [&>td]:p-2">
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
