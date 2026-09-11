import { ReactNode, type ButtonHTMLAttributes } from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/common/utils";
import Icon, { RotateColorEnum } from "../Icon";

const styleVariants = cva("relative flex items-center justify-center", {
  variants: {
    style: {
      default:
        "bg-button hover:bg-button-hover active:bg-button-clicked disabled:bg-button-disabled text-inverted-text-color",
      secondary:
        "bg-secondary-button hover:bg-secondary-button-hover active:bg-secondary-button-clicked disabled:bg-secondary-button-disabled text-default-text-color",
      none: "text-default-text-color",
    },
    size: {
      default: "w-full p-[6] rounded-[12] text-[16px]",
      sharp: "w-full p-[6] rounded-[4] text-[16px]",
      square: "size-[36] p-[6] rounded-[4] text-[16px]",
      fit: "w-fit px-[12] py-[6] rounded-[4] text-[16px]",
    },
  },
  defaultVariants: { style: "default", size: "default" },
});

type StyleVariants = VariantProps<typeof styleVariants>;
type ButtonProp = {
  children: ReactNode;
  loading?: boolean;
} & StyleVariants &
  Omit<ButtonHTMLAttributes<HTMLButtonElement>, "style">;

export default function Button({
  children,
  loading = false,
  disabled = false,
  style = "default",
  size = "default",
  onClick,
  type = "submit",
  className,
  ...props
}: ButtonProp) {
  const is_disabled = disabled || loading;

  let rotateColor = RotateColorEnum.DEFAULT;
  if (style === "secondary") rotateColor = RotateColorEnum.SECONDARY;

  return (
    <button
      className={cn(
        styleVariants({
          style,
          size,
        }),
        className,
      )}
      disabled={is_disabled}
      onClick={onClick}
      type={type}
      {...props}
    >
      <span className={cn(loading && "invisible")}>{children}</span>
      {loading && (
        <span className="absolute inset-0 flex items-center justify-center">
          <Icon
            svgPath="/loading/loading.svg"
            alt="Loading Icon"
            rotate={true}
            rotateColor={rotateColor}
          />
        </span>
      )}
    </button>
  );
}
