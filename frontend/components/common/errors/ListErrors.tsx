interface ListErrorProps {
  errors: string[];
}

export default function ListErrors({ errors }: ListErrorProps) {
  return (
    <div className="list-errors">
      <ul>
        {errors != null && errors.map((error, i) => <li key={i}>{error}</li>)}
      </ul>
    </div>
  );
}
