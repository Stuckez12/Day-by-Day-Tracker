interface RatingValueProps {
  value: string;
}

function RatingValueButton({ value }: RatingValueProps) {
  return (
    <div className="detect-click rate-button">
      <p className="rate-text">{value}</p>
    </div>
  );
}

export default RatingValueButton;
