import Image from "next/image";

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

  let styles = "";
  if (rotate) {
    switch (rotateColor) {
      case RotateColorEnum.DEFAULT:
        styles = "animate-spin brightness-0 invert";
        break;
      case RotateColorEnum.SECONDARY:
        styles = "animate-spin brightness-0";
        break;
    }
  }

  return (
    <Image
      className={styles}
      src={svgPath}
      alt={alt}
      width={width}
      height={height}
    />
  );
}
