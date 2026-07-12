import { Temporal } from "@js-temporal/polyfill";

import {
  getAccessToken,
  getBearerHeaders,
} from "@/lib/common/auth/getAccessToken";
import { Result, ValidationErrorProp } from "@/lib/interfaces/common";
import { RankingProp, RankingUIDataProp } from "@/lib/interfaces/ranking";
import { APICall, MustBeLoggedIn } from "@/lib/queries/base";

const API = new APICall(process.env.NEXT_PUBLIC_BASE_API_URL!);

const BASE_API_URL = process.env.NEXT_PUBLIC_BASE_API_URL;
const unauthorized = (): Result<never, ValidationErrorProp> => ({
  ok: false,
  error: {
    api_response: true,
    error_count: 1,
    errors: { api: ["Your session has expired. Please sign in again."] },
  },
});

async function rankingRequest<T>(
  path: string,
  init: RequestInit = {},
): Promise<Result<T, ValidationErrorProp>> {
  const authorization = await getBearerHeaders();
  if (!authorization) return unauthorized();

  const response = await fetch(`${BASE_API_URL}/api/v1/ranking${path}`, {
    ...init,
    headers: {
      ...authorization,
      ...(init.body ? { "Content-Type": "application/json" } : {}),
    },
  });
  const body = await response.json();

  if (response.ok) {
    return { ok: true, data: body };
  }

  return {
    ok: false,
    error: {
      api_response: true,
      error_count: 1,
      errors: { api: [body.detail ?? "Request failed"] },
    },
  };
}

export async function getRankTodayQuery(): Promise<
  Result<RankingProp, ValidationErrorProp>
> {
  const token = await getAccessToken();
  if (!token) {
    return {
      ok: false,
      error: MustBeLoggedIn,
    };
  }

  const response = await API.get({ url_path: "/today", token: token });
  const body = await response.json();

  if (response.ok) {
    return {
      ok: true,
      data: body,
    };
  }

  return {
    ok: false,
    error: {
      api_response: true,
      error_count: 1,
      errors: { api: body.detail },
    },
  };
}

export async function getAllRanksQuery() {
  const token = await getAccessToken();
  if (!token) {
    return MustBeLoggedIn;
  }

  const response = await API.get({ url_path: "/all", token: token });
  return rankingRequest<RankingProp[]>("/all");
}

export async function rankDayQuery(data: RankingUIDataProp) {
  const token = await getAccessToken();
  if (!token) {
    return MustBeLoggedIn;
  }

  const response = await API.post({
    url_path: "/today",
    body: data,
    token: token,
  });
  return rankingRequest<RankingProp>("", {
    method: "PUT",
    body: JSON.stringify({ ...data, ranking: data.ranking?.toString() }),
  });
}

export async function rankTodayNumberQuery({ ranking }: { ranking: number }) {
  return rankingRequest<RankingProp>("/rank", {
    method: "PUT",
    body: JSON.stringify({
      day: Temporal.Now.plainDateISO().toString(),
      ranking,
    }),
  });
}

export async function rankTodayNotesQuery({
  text_events,
  text_notes,
}: {
  text_events?: string;
  text_notes?: string;
}) {
  return rankingRequest<RankingProp>("/rank/notes", {
    method: "PUT",
    body: JSON.stringify({
      day: Temporal.Now.plainDateISO().toString(),
      text_events,
      text_notes,
    }),
  });
}
