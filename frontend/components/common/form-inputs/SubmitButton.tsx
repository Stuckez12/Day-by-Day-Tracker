interface TextInputProps {
  label: string;
}

export default function SubmitButton({ label }: TextInputProps) {
  return (
    <button className="submit-button" type="submit">
      {label}
    </button>
  );
}
