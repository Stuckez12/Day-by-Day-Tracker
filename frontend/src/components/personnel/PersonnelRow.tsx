import type { PersonnelRowProps } from "interfaces/personnel";

import SelectPersonnelButton from "components/personnel/SelectPersonnelButton";

import "styles/common/tables.scss";

function PersonnelRow({
  id,
  first_name,
  last_name,
  created_at,
  is_selected,
}: PersonnelRowProps) {
  const full_name = first_name + " " + last_name;

  const dis = is_selected == id;

  return (
    <tr className="table-row table-data-row" key={id}>
      <td>{id}</td>
      <td>{full_name}</td>
      <td>{created_at}</td>
      <td>{dis ? <span>X</span> : null}</td>
      <td>
        <SelectPersonnelButton id={id} />
      </td>
    </tr>
  );
}

export default PersonnelRow;
