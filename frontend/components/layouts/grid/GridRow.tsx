interface GridRowProps {
  children: React.ReactNode;
  width: number;
  height: number;
}

export default function GridRow({ children, width, height }: GridRowProps) {
  return (
    <div
      className="w-full h-full flex flex-row"
      style={{ maxWidth: `${width}px`, maxHeight: `${height}px` }}
    >
      {children}
    </div>
  );
}
