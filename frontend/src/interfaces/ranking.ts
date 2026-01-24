export interface RankingProps {
  id: string;
  personal_id: string;
  day: string;
  ranking: number;
  created_at: string;
  updated_at: string;
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
