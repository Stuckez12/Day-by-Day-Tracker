import Calendar from "@/components/calendar/Calendar";
import Button from "@/components/common/buttons/Button";
import Icon, { RotateColorEnum } from "@/components/common/Icon";
import PageWrapper from "@/components/common/PageWrapper";

export default function DevUI() {
  return (
    <PageWrapper>
      <br />
      <h1>Style Buttons</h1>
      <br />
      <div className="flex flex-row gap-x-2">
        <Button>Default Style</Button>
        <Button loading={true}>Default Style</Button>
        <Button disabled={true}>Disabled Default Style</Button>
      </div>
      <br />
      <div className="flex flex-row gap-x-2">
        <Button style="secondary">Secondary Style</Button>
        <Button style="secondary" loading={true}>
          Secondary Style
        </Button>
        <Button style="secondary" disabled={true}>
          Disabled Secondary Style
        </Button>
      </div>
      <br />
      <h1>Size Buttons</h1>
      <br />
      <div className="flex flex-row gap-x-2">
        <Button size="default">Size</Button>
        <Button size="sharp">Size</Button>
      </div>
      <br />
      <div className="flex flex-row gap-x-2">
        <Button size="square">1</Button>
        <Button size="fit">Size Fits Width</Button>
      </div>
      <br />
      <h1>Buttons W Icons</h1>
      <br />
      <div className="flex flex-row gap-x-2">
        <Button size="square">
          <Icon svgPath="/arrows/arrow-back-rounded.svg" alt="Icon" />
        </Button>
        <Button size="square">
          <Icon svgPath="/arrows/arrow-forward-rounded.svg" alt="Icon" />
        </Button>
        <Button size="square">
          <Icon svgPath="/loading/loading.svg" alt="Icon" rotate={true} />
        </Button>
      </div>
      <br />
      <div className="flex flex-row gap-x-2">
        <Button style="secondary" size="square">
          <Icon
            svgPath="/arrows/arrow-back-rounded.svg"
            alt="Icon"
            rotateColor={RotateColorEnum.SECONDARY}
          />
        </Button>
        <Button style="secondary" size="square">
          <Icon
            svgPath="/arrows/arrow-forward-rounded.svg"
            alt="Icon"
            rotateColor={RotateColorEnum.SECONDARY}
          />
        </Button>
        <Button style="secondary" size="square">
          <Icon
            svgPath="/loading/loading.svg"
            alt="Icon"
            rotate={true}
            rotateColor={RotateColorEnum.SECONDARY}
          />
        </Button>
      </div>
      <br />
      <h1>Calendar</h1>
      <br />
      <Calendar />
      <br />
      <br />
      <br />
      <br />
      <br />
      <br />
      <br />
    </PageWrapper>
  );
}
