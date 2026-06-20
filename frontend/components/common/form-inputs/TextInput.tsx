interface TextInputProps {
  name: string;
  type?: string;
  label: string;
  value: string;
  onChange: React.ChangeEventHandler<HTMLInputElement>;
  autoComplete?: string;
}

export default function TextInput({
  name,
  type,
  label,
  value,
  onChange,
  autoComplete,
}: TextInputProps) {
  let auto_complete = "off";

  if (autoComplete != null) {
    auto_complete = autoComplete;
  }

  let input_type = "text";

  if (type != null) {
    input_type = type;
  }

  return (
    <div className="text-input">
      <input
        type={input_type}
        name={name}
        value={value}
        onChange={onChange}
        placeholder=""
        autoComplete={auto_complete}
      />
      <label>{label}</label>
    </div>
  );
}
