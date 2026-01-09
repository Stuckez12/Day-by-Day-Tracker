import type { IDProps } from "interfaces/common";

import APICall from "scripts/api.ts";

function SelectPersonnelButton({ id }: IDProps) {
  const selectPersonnel = async (e: React.MouseEvent<HTMLButtonElement>) => {
    const clicked = e.currentTarget.dataset.id;
    if (!clicked) return;

    console.log("Clicked button:", clicked);

    const [success, response, err_message] = await APICall.put<null>(
      "/personal/select",
      {
        id: clicked,
      }
    );

    console.log(success, response, err_message);
  };

  return (
    <button data-id={id} onClick={selectPersonnel}>
      Select
    </button>
  );
}

export default SelectPersonnelButton;
