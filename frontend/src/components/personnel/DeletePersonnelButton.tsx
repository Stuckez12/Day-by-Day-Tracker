import { useContext } from "react";

import { ContextRefreshPersonnelList } from "contexts/ContextRefreshPersonnelList.tsx";

import type { IDProps } from "interfaces/common";

import APICall from "scripts/api.ts";

function DeletePersonnelButton({ id }: IDProps) {
  const { setRefreshList } = useContext(ContextRefreshPersonnelList);

  const selectPersonnel = async (e: React.MouseEvent<HTMLButtonElement>) => {
    const clicked = e.currentTarget.dataset.id;
    if (!clicked) return;

    const [success, _, err_message] = await APICall.delete<null>(
      "/personal?id=" + id,
    );

    if (success) {
      setRefreshList(true);
    }
  };

  return (
    <button data-id={id} onClick={selectPersonnel}>
      Delete
    </button>
  );
}

export default DeletePersonnelButton;
