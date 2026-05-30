interface PasswordInputProps {
  name: string;
  label: string;
  value: string;
  onChange: React.ChangeEventHandler<HTMLInputElement>;
  autoComplete?: string;
}

export default function PasswordInput({
  name,
  label,
  value,
  onChange,
  autoComplete,
}: PasswordInputProps) {
  let auto_complete = "off";

  if (autoComplete != null) {
    auto_complete = autoComplete;
  }

  return (
    <div className="text-input">
      <input
        type="password"
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
