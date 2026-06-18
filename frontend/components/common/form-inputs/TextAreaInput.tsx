interface TextAreaInputProps {
  name: string;
  value?: string;
  onChange: React.ChangeEventHandler<HTMLTextAreaElement>;
  autoComplete?: string;
}

export default function TextAreaInput({
  name,
  value,
  onChange,
  autoComplete,
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
        placeholder="Insert any event that happened today..."
        autoComplete={auto_complete}
      />
    </div>
  );
}
