import { useContext } from "react";

import { confirm } from "components/common/popup/PopupConfirmation.tsx"

import { ContextRefreshList } from "contexts/ContextRefreshList.tsx";

import type { PersonnelNameProps } from "interfaces/personnel";

import APICall from "scripts/api.ts";

function DeletePersonnelButton({ id, first_name, last_name }: PersonnelNameProps) {
  const { setRefreshList } = useContext(ContextRefreshList);

  const deletePersonnel = async (e: React.MouseEvent<HTMLButtonElement>) => {
    const clicked = e.currentTarget.dataset.id;
    if (!clicked) return;

    if (!(await confirm({
      title: "Personnel Deletion", 
      text_body: `Are you sure you want to delete ${first_name} ${last_name}?\n\nThis action is permanent and you will be unable to recover your account!`,
      proceed_label: "Delete",
      cancel_label: "Cancel"
    }))) {
      return;
    }

    const [success, _, err_message] = await APICall.delete<null>(
      "/personal?id=" + id,
    );

    if (success) {
      setRefreshList(true);
    } else {
      console.log(err_message);
    }
  };

  return (
    <button data-id={id} onClick={deletePersonnel}>
      Delete
    </button>
  );
}

export default DeletePersonnelButton;
