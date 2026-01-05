interface RatingValueProps {
  value: string;
}

function RatingValueButton({ value }: RatingValueProps) {
  return (
    <div className="detect-click">
      <p>{value}</p>
    </div>
  );
}

export default RatingValueButton;
