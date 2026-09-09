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
    <div className="relative my-4 w-full">
      <input
        className="peer w-full rounded-[5px] border-2 px-3 py-1.5 shadow-none"
        type="password"
        name={name}
        value={value}
        onChange={onChange}
        placeholder=""
        autoComplete={auto_complete}
      />
      <label className="pointer-events-none absolute top-[0.7rem] left-6 select-none rounded-lg bg-base px-2 text-[0.8rem] outline-0 transition-all duration-150 ease-in-out peer-placeholder-shown:left-2 peer-placeholder-shown:top-2 peer-placeholder-shown:text-base peer-focus:top-[0.7rem] peer-focus:left-6 peer-focus:text-[0.8rem] max-sm:peer-placeholder-shown:top-[0.6rem] max-sm:peer-placeholder-shown:text-[0.8rem]">
        {label}
      </label>
    </div>
  );
}
