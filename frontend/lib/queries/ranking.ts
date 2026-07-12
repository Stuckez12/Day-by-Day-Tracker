import { Temporal } from "@js-temporal/polyfill";

import { getAccessToken } from "@/lib/common/auth/getAccessToken";
import { Result, ValidationErrorProp } from "@/lib/interfaces/common";
import { RankingProp, RankingUIDataProp } from "@/lib/interfaces/ranking";
import { APICall, MustBeLoggedIn } from "@/lib/queries/base";

const API = new APICall(process.env.NEXT_PUBLIC_BASE_API_URL!);

export async function getRankTodayQuery(): Promise<
  Result<RankingProp, ValidationErrorProp>
> {
  const token = await getAccessToken();
  if (!token) {
    return MustBeLoggedIn;
  }

  return await API.get<RankingProp>({
    url_path: "/v1/ranking/today",
    token: token,
  });
}

export async function getAllRanksQuery(): Promise<
  Result<RankingProp[], ValidationErrorProp>
> {
  const token = await getAccessToken();
  if (!token) {
    return MustBeLoggedIn;
  }

  return await API.get<RankingProp[]>({
    url_path: "/v1/ranking/all",
    token: token,
  });
}

export async function rankDayQuery(
  data: RankingUIDataProp,
): Promise<Result<RankingProp, ValidationErrorProp>> {
  const token = await getAccessToken();
  if (!token) {
    return MustBeLoggedIn;
  }

  return await API.put<RankingProp>({
    url_path: "/v1/ranking",
    body: data,
    token: token,
  });
}

export async function rankTodayNumberQuery({
  ranking,
}: {
  ranking: number;
}): Promise<Result<RankingProp, ValidationErrorProp>> {
  const data = {
    day: Temporal.Now.plainDateISO().toString(),
    ranking: ranking,
  };
  const token = await getAccessToken();
  if (!token) {
    return MustBeLoggedIn;
  }

  return await API.put<RankingProp>({
    url_path: "/v1/ranking/rank",
    body: data,
    token: token,
  });
}

export async function rankTodayNotesQuery({
  text_events,
  text_notes,
}: {
  text_events?: string;
  text_notes?: string;
}) {
  const data = {
    day: Temporal.Now.plainDateISO().toString(),
    text_events: text_events,
    text_notes: text_notes,
  };
  const token = await getAccessToken();
  if (!token) {
    return MustBeLoggedIn;
  }

  return await API.put<RankingProp>({
    url_path: "/v1/ranking/rank/notes",
    body: data,
    token: token,
  });
}
