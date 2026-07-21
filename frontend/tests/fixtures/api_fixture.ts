import { afterEach, beforeEach, vi } from "vitest";
import {APICall, Request} from "@/lib/queries/base";
import { Result, ValidationErrorProp } from "@/lib/interfaces/common";

const apiCall = new APICall("");

export function APIFixture() {
    const mockAPIGet = vi.spyOn(apiCall, "get");

    async function mockGet(input: Request, output: Result<unknown, ValidationErrorProp>) {
        mockAPIGet.mockImplementation(async (i) => {
            if (i.url_path === input.url_path) {
                return output
            }

            throw new Error(`${i.url_path} was not mocked`);
        });
    }
}
