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
  is_selected: string;
}

export interface CreatePersonnelProps {
  first_name: string;
  last_name: string;
}

export interface PersonnelNameProps {
  id: string;
  first_name: string;
  last_name: string;
}
