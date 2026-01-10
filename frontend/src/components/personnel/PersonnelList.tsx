import { useEffect, useState } from "react";

import PersonnelRow from "components/personnel/PersonnelRow";

import type { PersonnelRowProps } from "interfaces/personnel.ts";

import APICall from "scripts/api.ts";

function PersonnelList() {
  const [personnels, setPersonnels] = useState<PersonnelRowProps[]>([]);

  useEffect(() => {
    const fetchPersonnel = async () => {
      const [success, data, _] = await APICall.get<PersonnelRowProps[]>(
        "/personal/all"
      );

      if (success) {
        setPersonnels(data!);
      }
    };

    fetchPersonnel();
  }, []);

  return (
    <table>
      <tr>
        <th>ID</th>
        <th>Full Name</th>
        <th>Date Created</th>
        <th>Select Personnel</th>
      </tr>
      {personnels.map(({ id, first_name, last_name, created_at }) => (
        <PersonnelRow
          id={id}
          first_name={first_name}
          last_name={last_name}
          created_at={created_at}
        />
      ))}
    </table>
  );
}

export default PersonnelList;
