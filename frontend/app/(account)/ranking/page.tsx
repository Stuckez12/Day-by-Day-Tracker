import Calendar from "@/components/calendar/Calendar";
import PageWrapper from "@/components/common/PageWrapper";

export default function RankingPage() {
  return (
    <PageWrapper>
      <div className="grid grid-cols-1 md:grid-cols-[60%_40%]">
        <Calendar />
        <div></div>
      </div>
    </PageWrapper>
  );
}
