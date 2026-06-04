export interface PersonnelProp {
  id: string;
  created_at: string;
  updated_at: string;

  email: string;
  password: string;

  first_name: string;
  last_name: string;
}

export type PersonnelLogin = Pick<PersonnelProp, "email" | "password">;
