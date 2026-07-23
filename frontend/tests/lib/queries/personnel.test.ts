import { describe, expect, it } from "vitest";

import { useAPIFixture } from "@/tests/fixtures/api_fixture";

import {
  getPersonnelQuery,
  updatePersonnelEmailQuery,
  updatePersonnelInfoQuery,
  updatePersonnelPasswordQuery,
} from "@/lib/queries/personnel";
import {
  UpdatePersonnelEmail,
  UpdatePersonnelInfo,
  UpdatePersonnelPassword,
} from "@/lib/interfaces/personnel";

const APIFixture = useAPIFixture();

describe("getPersonnelQuery", () => {
  it("returns successful", async () => {
    APIFixture.mockGet(
      {
        url_path: "/v1/personal/me",
      },
      { ok: true, data: {} },
    );
    await getPersonnelQuery();

    expect(APIFixture.mockAPIGet).toHaveBeenCalledWith({
      url_path: "/v1/personal/me",
      token: APIFixture.test_token,
    });
  });
});

describe("updatePersonnelInfoQuery", () => {
  it("returns successful", async () => {
    const data = {
      first_name: "First Name",
      last_name: "Last Name",
    } as UpdatePersonnelInfo;
    APIFixture.mockPut(
      {
        url_path: "/v1/personal/me/details",
      },
      { ok: true, data: {} },
    );
    await updatePersonnelInfoQuery(data);

    expect(APIFixture.mockAPIPut).toHaveBeenCalledWith({
      url_path: "/v1/personal/me/details",
      token: APIFixture.test_token,
      body: data,
    });
  });
});

describe("updatePersonnelEmailQuery", () => {
  it("returns successful", async () => {
    const data = {
      email: "test@email.com",
    } as UpdatePersonnelEmail;
    APIFixture.mockPut(
      {
        url_path: "/v1/personal/me/email",
      },
      { ok: true, data: {} },
    );
    await updatePersonnelEmailQuery(data);

    expect(APIFixture.mockAPIPut).toHaveBeenCalledWith({
      url_path: "/v1/personal/me/email",
      token: APIFixture.test_token,
      body: data,
    });
  });

  it("fails on invalid short email", async () => {
    const data = {
      email: "aaaa",
    } as UpdatePersonnelEmail;

    APIFixture.mockPut(
      {
        url_path: "/v1/personal/me/email",
      },
      { ok: true, data: {} },
    );
    const response = await updatePersonnelEmailQuery(data);
    expect(response).toMatchObject({
      ok: false,
      error: {
        api_response: false,
        error_count: 1,
        errors: { email: ["Insufficient email provided"] },
      },
    });
  });

  it("fails on invalid malformed email", async () => {
    const data = {
      email: "aaaaa",
    } as UpdatePersonnelEmail;

    APIFixture.mockPut(
      {
        url_path: "/v1/personal/me/email",
      },
      { ok: true, data: {} },
    );
    const response = await updatePersonnelEmailQuery(data);
    expect(response).toMatchObject({
      ok: false,
      error: {
        api_response: false,
        error_count: 1,
        errors: {
          email: ["Malformed email contains no @ symbol"],
        },
      },
    });
  });
});

describe("updatePersonnelPasswordQuery", () => {
  it("returns successful", async () => {
    const data = {
      current_password: "old-pw",
      new_password: "new-pw",
      confirm_password: "new-pw",
    } as UpdatePersonnelPassword;
    APIFixture.mockPut(
      {
        url_path: "/v1/personal/me/password",
      },
      { ok: true, data: {} },
    );
    await updatePersonnelPasswordQuery(data);

    expect(APIFixture.mockAPIPut).toHaveBeenCalledWith({
      url_path: "/v1/personal/me/password",
      token: APIFixture.test_token,
      body: data,
    });
  });

  it("fails on invalid password", async () => {
    // No password restrictions as of yet
    //
    // const data = {
    //   current_password: "old-pw",
    //   new_password: "new-pw",
    //   confirm_password: "new-pw",
    // } as UpdatePersonnelPassword;
    // APIFixture.mockPut(
    //   {
    //     url_path: "/v1/personal/me/email",
    //   },
    //   { ok: true, data: {} },
    // );
    // const response = await updatePersonnelPasswordQuery(data);
  });

  it("fails on new password mismatch", async () => {
    const data = {
      current_password: "old-pw",
      new_password: "new-pw",
      confirm_password: "different-pw",
    } as UpdatePersonnelPassword;

    APIFixture.mockPut(
      {
        url_path: "/v1/personal/me/email",
      },
      { ok: true, data: {} },
    );
    const response = await updatePersonnelPasswordQuery(data);
    expect(response).toMatchObject({
      ok: false,
      error: {
        api_response: false,
        error_count: 1,
        errors: {
          new_password: ["Passwords do not match"],
        },
      },
    });
  });
});
