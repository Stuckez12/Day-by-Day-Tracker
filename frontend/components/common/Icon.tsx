import Image from "next/image";
import { cn } from "@/lib/common/utils";

export enum RotateColorEnum {
  "DEFAULT",
  "SECONDARY",
}
interface IconProp {
  svgPath: string;
  alt: string;
  width?: number;
  height?: number;
  rotate?: boolean;
  rotateColor?: RotateColorEnum;
}

export default function Icon({
  svgPath,
  alt,
  width = 24,
  height = 24,
  rotate = false,
  rotateColor = RotateColorEnum.DEFAULT,
}: IconProp) {
  const basePath = "/assets/svg";
  if (basePath !== svgPath.slice(0, basePath.length)) {
    svgPath = basePath + svgPath;
  }

  const classes: string[] = [];

  if (rotate) classes.push("animate-spin");
  switch (rotateColor) {
    case RotateColorEnum.DEFAULT:
      classes.push("brightness-0 invert");
      break;
    case RotateColorEnum.SECONDARY:
      classes.push("brightness-0");
      break;
  }

  return (
    <Image
      className={cn(classes)}
      src={svgPath}
      alt={alt}
      width={width}
      height={height}
    />
  );
}
