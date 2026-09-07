import { RankingProp } from "@/lib/interfaces/ranking";

function RatingRow({ rank }: { rank: RankingProp }) {
  const has_text =
    rank.text_events !== undefined || rank.text_notes !== undefined;

  return (
    <tr className="odd:bg-[#e9e9e9] even:bg-[#f3f3f3] hover:bg-[#d4d4d4] [&>td]:border [&>td]:border-[#ddd] [&>td]:p-2">
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
