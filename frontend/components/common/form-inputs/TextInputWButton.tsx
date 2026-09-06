import type { ChangeEventHandler, MouseEventHandler } from "react";
import Button from "../buttons/Button";

interface TextInputWButtonProps {
  name: string;
  type?: string;
  label: string;
  value: string;
  onChange: ChangeEventHandler<HTMLInputElement>;
  button_label: string;
  onSubmit: MouseEventHandler<HTMLButtonElement>;
  autoComplete?: string;
  isLoading?: boolean;
}

export default function TextInputWButton({
  name,
  type,
  label,
  value,
  onChange,
  button_label,
  onSubmit,
  autoComplete,
  isLoading = false,
}: TextInputWButtonProps) {
  let auto_complete = "off";
  if (autoComplete != null) auto_complete = autoComplete;

  let input_type = "text";
  if (type != null) input_type = type;

  return (
    <div className="text-input-button">
      <input
        type={input_type}
        name={name}
        value={value}
        onChange={onChange}
        placeholder=""
        autoComplete={auto_complete}
      />
      <label>{label}</label>
      <Button onClick={onSubmit} loading={isLoading}>
        {button_label}
      </Button>
    </div>
  );
}
