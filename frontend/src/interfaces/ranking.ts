export interface RankingProps {
  id: string;
  personal_id: string;

  day: string;
  ranking: number;

  text_events: string;
  text_notes: string;

  created_at: string;
  updated_at: string;
}

export interface RankingTextBoxProps {
  text_events: string;
  text_notes: string;
}

export interface UpdateRankingProps {
  id: string;
  day: string;
  ranking: number;
}

export interface OptionalRankingProps {
  ranking: number | null;
}

export interface RankingRowProps {
  day: string;
  ranking: number | null;
}
