"use client";

export default function CalendarHeader({ header }: { header: string }) {
  return (
    <div className="w-full h-full flex items-center justify-center font-bold p-[4]">
      <span>{header}</span>
    </div>
  );
}
