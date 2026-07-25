import { describe, expect, it } from "vitest";

import { validateEmail } from "@/lib/common/validation/validateEmail";

describe("validateEmail", () => {
  it("returns successful", async () => {
    const response = validateEmail("test@email.com");
    expect(response.length).toBe(0);
  });

  it("fails on short email", async () => {
    const response = validateEmail("aaaa");
    expect(response.length).toBe(1);
    expect(response[0]).toBe("Insufficient email provided");
  });

  it("fails when missing @ symbol", async () => {
    const response = validateEmail("aaaaa");
    expect(response.length).toBe(1);
    expect(response[0]).toBe("Malformed email contains no @ symbol");
  });
});
