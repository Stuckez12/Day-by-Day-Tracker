import { Temporal } from "@js-temporal/polyfill";

import { getBearerHeaders } from "@/lib/common/auth/getAccessToken";
import { Result, ValidationErrorProp } from "@/lib/interfaces/common";
import { RankingProp, RankingUIDataProp } from "@/lib/interfaces/ranking";

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

  return response.ok
    ? { ok: true, data: body }
    : {
        ok: false,
        error: {
          api_response: true,
          error_count: 1,
          errors: { api: [body.detail ?? "Request failed"] },
        },
      };
}

export function getRankTodayQuery() {
  return rankingRequest<RankingProp>("/today");
}

export function getAllRanksQuery() {
  return rankingRequest<RankingProp[]>("/all");
}

export function rankDayQuery(data: RankingUIDataProp) {
  return rankingRequest<RankingProp>("", {
    method: "PUT",
    body: JSON.stringify({ ...data, ranking: data.ranking?.toString() }),
  });
}

export function rankTodayNumberQuery({ ranking }: { ranking: number }) {
  return rankingRequest<RankingProp>("/rank", {
    method: "PUT",
    body: JSON.stringify({ day: Temporal.Now.plainDateISO().toString(), ranking }),
  });
}

export function rankTodayNotesQuery({
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
