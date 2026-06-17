import { UUID } from "crypto";

export interface PersonnelProp {
  id: UUID;
  created_at: string;
  updated_at: string;

  email: string;
  password: string;

  first_name: string;
  last_name: string;
}

export type PersonnelLogin = Pick<PersonnelProp, "email" | "password">;
export type PartialPersonnelProp = Partial<PersonnelProp>;

export type UpdatePersonnelInfo = Pick<
  PersonnelProp,
  "first_name" | "last_name"
>;
export type UpdatePersonnelEmail = Pick<PersonnelProp, "email">;
export interface UpdatePersonnelPassword {
  current_password: string;
  new_password: string;
  confirm_password: string;
}
