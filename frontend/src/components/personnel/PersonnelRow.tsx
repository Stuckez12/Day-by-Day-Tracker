import type { PersonnelRowProps } from "interfaces/personnel";

function PersonnelRow({
  id,
  first_name,
  last_name,
  created_at,
}: PersonnelRowProps) {
  const full_name = first_name + " " + last_name;

  return (
    <tr>
      <td>{id}</td>
      <td>{full_name}</td>
      <td>{created_at}</td>
    </tr>
  );
}

export default PersonnelRow;
