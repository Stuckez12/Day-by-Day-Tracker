"use client";

import CalendarProvider from "@/components/calendar/CalendarProvider";
import PageWrapper from "@/components/common/PageWrapper";
import EditCalendarDataForm from "@/components/forms/multiblock/EditCalendarDataForm";

export default function RankingPage() {
  return (
    <PageWrapper>
      <CalendarProvider>
        <EditCalendarDataForm />
      </CalendarProvider>
    </PageWrapper>
  );
}
