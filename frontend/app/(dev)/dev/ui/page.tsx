import Calendar from "@/components/calendar/Calendar";
import Button from "@/components/common/buttons/Button";
import Icon from "@/components/common/Icon";
import PageWrapper from "@/components/common/PageWrapper";

export default function DevUI() {
  return (
    <PageWrapper>
      <br />
      <br />
      <br />
      <br />
      <br />
      <Button>Button</Button>
      <br />
      <Button style="secondary" size="fit">
        <Icon svgPath="/arrows/arrow-forward-rounded.svg" alt="Forward Arrow" />
        <span>Hello</span>
      </Button>
      <br />
      <br />
      <br />
      <br />
      <br />
      <br />
      <br />
      <br />
      <br />
      <br />
      <br />
      <br />
      <br />
      <br />
      <br />
      <Calendar />
      <br />
      <br />
      <br />
      <br />
      <br />
    </PageWrapper>
  );
}
