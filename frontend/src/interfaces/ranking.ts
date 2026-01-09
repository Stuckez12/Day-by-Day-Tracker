export interface RankingProps {
  id: string;
  personal_id: string;
  day: string;
  ranking: number;
  created_at: string;
  updated_at: string;
}

export interface OptionalRankingProps {
  ranking: number | null;
}
