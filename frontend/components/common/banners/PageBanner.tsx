import PageWrapper from "@/components/common/PageWrapper";
import { cn } from "@/lib/common/utils";

interface PageBannerProps {
  message: string;
  type: string;
}

export default function PageBanner({ message, type }: PageBannerProps) {
  if (!message) return null;

  let bgCol = "";
  switch (type) {
    case "INFO":
      bgCol = "bg-banner-info";
      break;
    case "WARNING":
      bgCol = "bg-banner-warning";
      break;
  }

  return (
    <div className={cn("w-full h-9", bgCol)}>
      <PageWrapper>
        <p className="leading-9 text-inverted-text-color">{message}</p>
      </PageWrapper>
    </div>
  );
}
