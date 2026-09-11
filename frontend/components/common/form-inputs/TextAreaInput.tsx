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
    <div className="relative my-4 w-full">
      <textarea
        className="min-h-[4em] w-full rounded-[5px] border-2 px-3 py-1.5 shadow-none"
        name={name}
        value={final_value}
        onChange={onChange}
        placeholder={placeholder}
        autoComplete={auto_complete}
      />
    </div>
  );
}
