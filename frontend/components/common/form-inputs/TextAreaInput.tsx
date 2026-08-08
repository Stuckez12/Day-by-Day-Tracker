interface TextAreaInputProps {
  name: string;
  value?: string;
  onChange: React.ChangeEventHandler<HTMLTextAreaElement>;
  autoComplete?: string;
  placeholder?: string;
}

export default function TextAreaInput({
  name,
  value,
  onChange,
  autoComplete,
  placeholder = "Insert any event that happened today...",
}: TextAreaInputProps) {
  let auto_complete = "off";

  if (autoComplete != null) {
    auto_complete = autoComplete;
  }

  let final_value = "";

  if (value != undefined) {
    final_value = value;
  }

  return (
    <div className="textarea-input">
      <textarea
        name={name}
        value={final_value}
        onChange={onChange}
        placeholder={placeholder}
        autoComplete={auto_complete}
      />
    </div>
  );
}
