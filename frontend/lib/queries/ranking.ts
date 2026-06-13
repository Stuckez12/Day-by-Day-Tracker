"use client";

import { Temporal } from "@js-temporal/polyfill";
import Cookies from "js-cookie";
import { err, ok, Result } from "neverthrow";

import { ValidationErrorProp } from "@/lib/interfaces/common";
import { RankingProp } from "@/lib/interfaces/ranking";

const base_url = process.env.NEXT_PUBLIC_API_URL;

export async function getRankTodayQuery(): Promise<
  Result<RankingProp, ValidationErrorProp>
> {
  const token = Cookies.get("personnel_id");
  const response = await fetch(`${base_url}/api/v1/ranking/today`, {
    method: "GET",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      Cookie: `personnel_id=${token}`,
    },
  });
  const body = await response.json();

  if (response.ok) {
    return ok(body);
  }

  return err({
    api_response: true,
    error_count: 1,
    errors: { api: body.detail },
  });
}

interface RankTodayNumberQueryProps {
  ranking: number;
}

export async function rankTodayNumberQuery({
  ranking,
}: RankTodayNumberQueryProps): Promise<
  Result<RankingProp, ValidationErrorProp>
> {
  const form = {
    day: Temporal.Now.plainDateISO().toString(),
    ranking: ranking,
  };

  const token = Cookies.get("personnel_id");
  const response = await fetch(`${base_url}/api/v1/ranking/rank`, {
    method: "PUT",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      Cookie: `personnel_id=${token}`,
    },
    body: JSON.stringify(form),
  });
  const body = await response.json();

  console.log(body);
  console.log("-------------------------------------");

  if (response.ok) {
    return ok(body);
  }

  return err({
    api_response: true,
    error_count: 1,
    errors: { api: body.detail },
  });
}

interface RankTodayNotesQueryProps {
  text_events: string;
  text_notes: string;
}

export async function rankTodayNotesQuery({
  text_events,
  text_notes,
}: RankTodayNotesQueryProps): Promise<
  Result<RankingProp, ValidationErrorProp>
> {
  const form = {
    day: Temporal.Now.plainDateISO().toString(),
    text_events: text_events,
    text_notes: text_notes,
  };

  const token = Cookies.get("personnel_id");
  const response = await fetch(`${base_url}/api/v1/ranking/rank/notes`, {
    method: "PUT",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      Cookie: `personnel_id=${token}`,
    },
    body: JSON.stringify(form),
  });
  const body = await response.json();

  console.log(body);
  console.log("-------------------------------------");

  if (response.ok) {
    return ok(body);
  }

  return err({
    api_response: true,
    error_count: 1,
    errors: { api: body.detail },
  });
}
