import "@/styles/tracker/ranking.scss";
import { ReactNode } from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/common/utils";

const styleVariants = cva("flex items-center justify-center", {
  variants: {
    style: {
      default: "bg-[#007ea7] hover:bg-[#00a1d6] active:bg-[#00a8e8] text-white",
      secondary:
        "bg-[#f0f0f0] hover:bg-[#f3f3f3] active:bg-[#f6f6f6] text-black",
    },
    size: {
      default: "w-full p-[6] rounded-[12] text-[16px]",
      sharp: "w-full p-[6] rounded-[4] text-[16px]",
      square: "size-[36] p-[6] rounded-[4] text-[16px]",
    },
    icon: {
      default: "",
    },
  },
  defaultVariants: { style: "default", size: "default", icon: "default" },
});

type StyleVariants = VariantProps<typeof styleVariants>;
type ButtonProp = {
  children: ReactNode;
  onClick?: () => void;
} & StyleVariants & {};

export default function Button({
  children,
  style = "default",
  size = "default",
  icon = "default",
  onClick,
}: ButtonProp) {
  return (
    <div
      className={cn(
        styleVariants({
          style,
          size,
          icon,
        }),
      )}
      onClick={onClick}
    >
      {children}
    </div>
  );
}
