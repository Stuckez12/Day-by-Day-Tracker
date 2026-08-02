interface IconProp {
  svgPath: string;
  alt: string;
  width?: number;
  height?: number;
}

export default function Icon({
  svgPath,
  alt,
  width = 24,
  height = 24,
}: IconProp) {
  const basePath = "/assets/svg";

  if (basePath !== svgPath.slice(0, basePath.length)) {
    svgPath = basePath + svgPath;
  }

  return <img src={svgPath} alt={alt} width={width} height={height} />;
}
