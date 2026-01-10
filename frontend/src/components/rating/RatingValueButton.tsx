import clsx from "clsx";

interface RatingValueProps {
  value: string;
  selected: number | null;
}

function RatingValueButton({ value, selected }: RatingValueProps) {
  const btn_active = value == String(selected);

  return (
    <div
      className={clsx("detect-click rate-button", {
        "is-selected": btn_active,
      })}
    >
      <p className="rate-text">{value}</p>
    </div>
  );
}

export default RatingValueButton;
