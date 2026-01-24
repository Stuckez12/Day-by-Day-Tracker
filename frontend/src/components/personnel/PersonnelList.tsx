import { useContext, useEffect, useState } from "react";

import PersonnelRow from "components/personnel/PersonnelRow";

import { ContextRefreshPersonnelList } from "contexts/ContextRefreshPersonnelList.tsx";

import type { IDProps } from "interfaces/common";
import type { PersonnelRowProps } from "interfaces/personnel.ts";

import APICall from "scripts/api.ts";

import "styles/common/tables.scss";

function PersonnelList() {
  const [personnels, setPersonnels] = useState<PersonnelRowProps[]>([]);
  const [selected_personnel, setSelectedPersonnels] = useState<IDProps>();

  const { refreshList, setRefreshList } = useContext(
    ContextRefreshPersonnelList,
  );

  useEffect(() => {
    if (!refreshList) {
      return;
    }

    const fetchPersonnel = async () => {
      const [success, data, _] =
        await APICall.get<PersonnelRowProps[]>("/personal/all");

      if (success) {
        setPersonnels(data!);
      }
    };

    const fetchSelectedPersonnel = async () => {
      const [success, data, _] =
        await APICall.get<PersonnelRowProps>("/personal/me");

      if (success) {
        setSelectedPersonnels(data!);
      }
    };

    fetchPersonnel();
    fetchSelectedPersonnel();
    setRefreshList(false);
  }, [refreshList]);

  const selected = selected_personnel ? selected_personnel.id : "";

  return (
    <div className="table-base">
      <table>
        <tr className="table-row table-header-row">
          <th>ID</th>
          <th>Full Name</th>
          <th>Date Created</th>
          <th>Selected</th>
          <th>Select Personnel</th>
        </tr>
        {personnels.map(({ id, first_name, last_name, created_at }) => (
          <PersonnelRow
            id={id}
            first_name={first_name}
            last_name={last_name}
            created_at={created_at}
            is_selected={selected}
          />
        ))}
      </table>
    </div>
  );
}

export default PersonnelList;
