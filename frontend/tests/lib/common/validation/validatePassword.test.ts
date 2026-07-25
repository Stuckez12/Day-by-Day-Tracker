import { describe, expect, it } from "vitest";

import { validatePassword } from "@/lib/common/validation/validatePassword";

describe("validatePassword", () => {
  it("returns successful", async () => {
    const response = validatePassword("Password1.");
    expect(response.length).toBe(0);
  });
});
