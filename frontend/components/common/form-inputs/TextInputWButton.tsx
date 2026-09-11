import type { ChangeEventHandler, MouseEventHandler } from "react";
import Button from "../buttons/Button";
import { cn } from "@/lib/common/utils";

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
  const isLabelFloating = value.length > 0;

  return (
    <div className="relative my-4 w-full">
      <input
        className="peer w-[min(80%,calc(100%-96px))] rounded-l-[5px] border-2 px-3 py-1.5 shadow-none"
        type={input_type}
        name={name}
        value={value}
        onChange={onChange}
        placeholder=""
        autoComplete={auto_complete}
      />
      <label
        className={cn(
          "pointer-events-none absolute left-2 top-2 select-none rounded-lg bg-base px-2 text-base transition-all duration-150 ease-in-out peer-focus:left-6 peer-focus:top-[-0.7rem] peer-focus:text-[0.8rem] max-[576px]:text-[0.8rem]",
          isLabelFloating && "left-6 top-[-0.7rem] text-[0.8rem]",
        )}
      >
        {label}
      </label>
      <Button
        className="inline-flex w-[20%] min-w-24 rounded-l-none rounded-r-lg px-0 py-2"
        onClick={onSubmit}
        loading={isLoading}
      >
        {button_label}
      </Button>
    </div>
  );
}
