"use client";

export default function CalendarHeader({ header }: { header: string }) {
  return (
    <div className="w-full h-full flex p-[4]">
      <span>{header}</span>
    </div>
  );
}
