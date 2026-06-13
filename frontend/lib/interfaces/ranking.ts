export interface RankingProp {
  id: string;
  created_at: string;
  updated_at: string;

  personal_id: string;

  day: string;
  ranking: number;

  text_events?: string;
  text_notes?: string;
}

export type RankingUIDataProp = Pick<
  RankingProp,
  "day" | "text_events" | "text_notes"
> &
  Partial<Pick<RankingProp, "ranking">>;
