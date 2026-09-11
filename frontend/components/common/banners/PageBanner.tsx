"use client";

import PageWrapper from "@/components/common/PageWrapper";
import { cn } from "@/lib/common/utils";
import { useState } from "react";
import Button from "../buttons/Button";
import Icon, { RotateColorEnum } from "../Icon";

interface PageBannerProps {
  message: string;
  type: string;
}

export default function PageBanner({ message, type }: PageBannerProps) {
  const [visible, setVisible] = useState<boolean>(true);
  if (!message) return null;
  if (!visible) return null;

  let bgCol = "";
  switch (type) {
    case "INFO":
      bgCol = "bg-banner-info";
      break;
    case "WARNING":
      bgCol = "bg-banner-warning";
      break;
  }

  function onClick() {
    setVisible(false);
  }

  return (
    <div className={cn("w-full h-9", bgCol)}>
      <PageWrapper>
        <div className="flex flex-row">
          <p className="leading-9 text-inverted-text-color px-3">{message}</p>
          <Button
            className="ml-auto"
            style="none"
            size="square"
            loading={false}
            disabled={false}
            onClick={onClick}
          >
            <Icon svgPath="/close/x.svg" alt="Exit Icon" rotate={false} />
          </Button>
        </div>
      </PageWrapper>
    </div>
  );
}
