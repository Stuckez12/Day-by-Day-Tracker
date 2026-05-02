export interface APIPersonnelProps {
  id: string;
  first_name: string;
  last_name: string;
  created_at: string;
  updated_at: string;
}

export interface PersonnelRowProps {
  id: string;
  first_name: string;
  last_name: string;
}

export interface PersonnelProps {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
}

export interface PersonnelPropsContext {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
}

export interface PersonnelDetailsProps {
  first_name: string;
  last_name: string;
}

export interface PersonnelEmailProps {
  email: string;
}

export interface PersonnelPasswordUpdateProps {
  current_password: string;
  new_password: string;
  confirm_password: string;
}
