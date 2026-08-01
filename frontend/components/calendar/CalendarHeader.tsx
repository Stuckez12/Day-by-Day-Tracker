"use client";

export default function CalendarHeader({ header }: { header: string }) {
  return (
    <div className="w-full h-full">
      <p>{header}</p>
    </div>
  );
}
