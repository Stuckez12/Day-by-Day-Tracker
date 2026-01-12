import type { PersonnelRowProps } from "interfaces/personnel";

import SelectPersonnelButton from "components/personnel/SelectPersonnelButton";

function PersonnelRow({
  id,
  first_name,
  last_name,
  created_at,
}: PersonnelRowProps) {
  const full_name = first_name + " " + last_name;

  return (
    <tr key={id}>
      <td>{id}</td>
      <td>{full_name}</td>
      <td>{created_at}</td>
      <td>
        <SelectPersonnelButton id={id} />
      </td>
    </tr>
  );
}

export default PersonnelRow;
