import { MouseEventHandler } from "react";

interface TextInputProps {
  label: string;
  onSubmit: MouseEventHandler<HTMLButtonElement>;
}

export default function SubmitButton({ label, onSubmit }: TextInputProps) {
  return (
    <button className="submit-button" onClick={onSubmit}>
      {label}
    </button>
  );
}
