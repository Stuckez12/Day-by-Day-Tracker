import { useContext } from "react";

import { ContextRefreshList } from "contexts/ContextRefreshList.tsx";

import type { IDProps } from "interfaces/common";

import APICall from "scripts/api.ts";

function SelectPersonnelButton({ id }: IDProps) {
  const { setRefreshList } = useContext(ContextRefreshList);

  const selectPersonnel = async (e: React.MouseEvent<HTMLButtonElement>) => {
    const clicked = e.currentTarget.dataset.id;
    if (!clicked) return;

    const [success, _, err_message] = await APICall.put<null>(
      "/personal/select",
      {
        id: clicked,
      },
    );

    if (success) {
      setRefreshList(true);
    }
  };

  return (
    <button data-id={id} onClick={selectPersonnel}>
      Select
    </button>
  );
}

export default SelectPersonnelButton;
