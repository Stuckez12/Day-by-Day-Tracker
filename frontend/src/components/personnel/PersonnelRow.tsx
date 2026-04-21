import type { PersonnelRowProps } from "interfaces/personnel";

import SelectPersonnelButton from "components/personnel/SelectPersonnelButton";
import DeletePersonnelButton from "components/personnel/DeletePersonnelButton";

import "styles/common/tables.scss";

function PersonnelRow({
  id,
  first_name,
  last_name,
  is_selected,
}: PersonnelRowProps) {
  const full_name = first_name + " " + last_name;
  const dis = is_selected == id;

  return (
    <tr className="table-row table-data-row" key={id}>
      <td>{full_name}</td>
      <td>
        <SelectPersonnelButton id={id} />
      </td>
      <td>
        <DeletePersonnelButton id={id} first_name={first_name} last_name={last_name} />
      </td>
    </tr>
  );
}

export default PersonnelRow;
