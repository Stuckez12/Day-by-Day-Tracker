import { MouseEventHandler } from "react";

interface TextInputWButtonProps {
  name: string;
  type?: string;
  label: string;
  value: string;
  onChange: React.ChangeEventHandler<HTMLInputElement>;
  button_label: string;
  onSubmit: MouseEventHandler<HTMLButtonElement>;
  autoComplete?: string;
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
}: TextInputWButtonProps) {
  let auto_complete = "off";

  if (autoComplete != null) {
    auto_complete = autoComplete;
  }

  let input_type = "text";

  if (type != null) {
    input_type = type;
  }

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
      <button onClick={onSubmit}>{button_label}</button>
    </div>
  );
}
