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
      <Button style="secondary" size="square">
        <Icon svgPath="/arrows/arrow-forward-rounded.svg" alt="Forward Arrow" />
      </Button>
    </PageWrapper>
  );
}
