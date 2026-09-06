import { ReactNode, type ButtonHTMLAttributes } from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/common/utils";
import Icon, { RotateColorEnum } from "../Icon";

const styleVariants = cva("relative flex items-center justify-center", {
  variants: {
    style: {
      default:
        "bg-[#007ea7] hover:bg-[#00a1d6] active:bg-[#00a8e8] disabled:bg-[#004d66] text-white",
      secondary:
        "bg-[#f0f0f0] hover:bg-[#f3f3f3] active:bg-[#f6f6f6] disabled:bg-[#c7c7c7] text-black",
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
