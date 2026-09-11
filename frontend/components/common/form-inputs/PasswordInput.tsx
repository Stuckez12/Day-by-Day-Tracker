import { cn } from "@/lib/common/utils";

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

  const isLabelFloating = value.length > 0;

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
      <label
        className={cn(
          "pointer-events-none absolute left-2 top-2 select-none rounded-lg bg-base px-2 text-base outline-0 transition-all duration-150 ease-in-out peer-focus:left-6 peer-focus:top-[-0.7rem] peer-focus:text-[0.8rem] max-sm:top-[0.6rem] max-sm:text-[0.8rem] max-sm:peer-focus:top-[-0.7rem]",
          isLabelFloating &&
            "left-6 top-[-0.7rem] text-[0.8rem] max-sm:top-[-0.7rem]",
        )}
      >
        {label}
      </label>
    </div>
  );
}
