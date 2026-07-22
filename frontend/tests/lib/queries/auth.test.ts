import { describe, expect, it } from "vitest";

import { PersonnelLogin } from "@/lib/interfaces/personnel";
import { personnelLoginQuery } from "@/lib/queries/auth";
import { useAPIFixture } from "@/tests/fixtures/api_fixture";

const APIFixture = useAPIFixture();

describe("personnelLoginQuery", () => {
  it("returns successful", async () => {
    const data = {
      email: "test@email.com",
      password: "Password1.",
    } as PersonnelLogin;

    APIFixture.mockPost(
      {
        url_path: "/v1/auth/login",
      },
      { ok: true, data: {} },
    );
    await personnelLoginQuery(data);

    expect(APIFixture.mockAPIPost).toHaveBeenCalledWith({
      url_path: "/v1/auth/login",
      body: data,
    });
  });
});
