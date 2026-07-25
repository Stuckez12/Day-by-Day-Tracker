import { Temporal } from "@js-temporal/polyfill";
import { describe, expect, it } from "vitest";

import { useAPIFixture } from "@/tests/fixtures/api_fixture";

import { MustBeLoggedIn } from "@/lib/queries/base";
import {
  getRankTodayQuery,
  getAllRanksQuery,
  rankDayQuery,
  rankTodayNumberQuery,
  rankTodayNotesQuery,
} from "@/lib/queries/ranking";
import { RankingUIDataProp } from "@/lib/interfaces/ranking";
import { NEXT_BODY_SUFFIX } from "next/dist/lib/constants";

const APIFixture = useAPIFixture();

describe("getRankTodayQuery", () => {
  it("returns successful", async () => {
    const token = APIFixture.mockToken();
    APIFixture.mockGet(
      {
        url_path: "/v1/ranking/today",
      },
      { ok: true, data: {} },
    );
    await getRankTodayQuery();

    expect(APIFixture.mockAPIGet).toHaveBeenCalledWith({
      url_path: "/v1/ranking/today",
      token: token,
    });
  });

  it("fails with no token", async () => {
    APIFixture.mockGet(
      {
        url_path: "/v1/ranking/today",
      },
      { ok: true, data: {} },
    );
    const response = await getRankTodayQuery();
    expect(response).toBe(MustBeLoggedIn);
  });
});

describe("getAllRanksQuery", () => {
  it("returns successful", async () => {
    const token = APIFixture.mockToken();
    APIFixture.mockGet(
      {
        url_path: "/v1/ranking/all",
      },
      { ok: true, data: {} },
    );
    await getAllRanksQuery();

    expect(APIFixture.mockAPIGet).toHaveBeenCalledWith({
      url_path: "/v1/ranking/all",
      token: token,
    });
  });

  it("fails with no token", async () => {
    APIFixture.mockGet(
      {
        url_path: "/v1/ranking/all",
      },
      { ok: true, data: {} },
    );
    const response = await getAllRanksQuery();
    expect(response).toBe(MustBeLoggedIn);
  });
});

describe("rankDayQuery", () => {
  it("returns successful", async () => {
    const data = {
      day: Temporal.Now.plainDateISO().toString(),
      text_events: "data",
      text_notes: "data",
    } as RankingUIDataProp;
    const token = APIFixture.mockToken();
    APIFixture.mockPut(
      {
        url_path: "/v1/ranking",
      },
      { ok: true, data: {} },
    );
    await rankDayQuery(data);

    expect(APIFixture.mockAPIPut).toHaveBeenCalledWith({
      url_path: "/v1/ranking",
      token: token,
      body: data,
    });
  });

  it("fails with no token", async () => {
    const data = {
      day: Temporal.Now.plainDateISO().toString(),
      text_events: "data",
      text_notes: "data",
    } as RankingUIDataProp;
    APIFixture.mockPut(
      {
        url_path: "/v1/ranking",
      },
      { ok: true, data: {} },
    );
    const response = await rankDayQuery(data);
    expect(response).toBe(MustBeLoggedIn);
  });
});

describe("rankTodayNumberQuery", () => {
  it("returns successful", async () => {
    const data = { ranking: 5 };
    const token = APIFixture.mockToken();
    APIFixture.mockPut(
      {
        url_path: "/v1/ranking/rank",
      },
      { ok: true, data: {} },
    );
    await rankTodayNumberQuery(data);

    expect(APIFixture.mockAPIPut).toHaveBeenCalledWith({
      url_path: "/v1/ranking/rank",
      token: token,
      body: { ...data, day: expect.stringMatching(/^\d{4}-\d{2}-\d{2}$/) },
    });
  });

  it("fails with no token", async () => {
    const data = { ranking: 5 };
    APIFixture.mockPut(
      {
        url_path: "/v1/ranking/rank",
      },
      { ok: true, data: {} },
    );
    const response = await rankTodayNumberQuery(data);
    expect(response).toBe(MustBeLoggedIn);
  });
});

describe("rankTodayNotesQuery", () => {
  it("returns successful", async () => {
    const data = { text_events: "event", text_notes: "notes" };
    const token = APIFixture.mockToken();
    APIFixture.mockPut(
      {
        url_path: "/v1/ranking/rank/notes",
      },
      { ok: true, data: {} },
    );
    await rankTodayNotesQuery(data);

    expect(APIFixture.mockAPIPut).toHaveBeenCalledWith({
      url_path: "/v1/ranking/rank/notes",
      token: token,
      body: { ...data, day: expect.stringMatching(/^\d{4}-\d{2}-\d{2}$/) },
    });
  });

  it("fails with no token", async () => {
    const data = { text_events: "event", text_notes: "notes" };
    APIFixture.mockPut(
      {
        url_path: "/v1/ranking/rank/notes",
      },
      { ok: true, data: {} },
    );
    const response = await rankTodayNotesQuery(data);
    expect(response).toBe(MustBeLoggedIn);
  });
});
