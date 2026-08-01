interface GridItemProps {
  children: React.ReactNode;
  width: number;
  height: number;
}

export default function GridItem({ children, width, height }: GridItemProps) {
  return (
    <div
      style={{
        width: `${width}px`,
        height: `${height}px`,
        maxWidth: `${width}px`,
        maxHeight: `${height}px`,
      }}
    >
      {children}
    </div>
  );
}
