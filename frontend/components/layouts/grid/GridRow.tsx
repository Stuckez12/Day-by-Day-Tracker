import clsx from "clsx";
import { CSSProperties } from "react";

interface GridRowProps {
  children: React.ReactNode;
  width: number;
  height: number;
  classes?: string;
  styles?: CSSProperties;
}

export default function GridRow({
  children,
  width,
  height,
  classes,
  styles,
}: GridRowProps) {
  const stylings: CSSProperties = {
    maxWidth: `${width}px`,
    maxHeight: `${height}px`,
    ...styles,
  };

  return (
    <div style={stylings} className="yahoo">
      <div className={clsx("w-full h-full flex flex-row", classes)}>
        {children}
      </div>
    </div>
  );
}
