import { afterEach, beforeEach, vi } from "vitest";

import { APICall, Request } from "@/lib/queries/base";
import { Result, ValidationErrorProp } from "@/lib/interfaces/common";

vi.mock("@/lib/common/auth/getAccessToken", () => ({
  getAccessToken: vi.fn(),
}));

import { getAccessToken } from "@/lib/common/auth/getAccessToken";

interface MockRequest {
  url: string;
  output: Result<unknown, ValidationErrorProp>;
}

export function useAPIFixture() {
  const mockAPIGet = vi.spyOn(APICall.prototype, "get");
  let mockedGetRequests: MockRequest[] = [];
  const mockAPIPost = vi.spyOn(APICall.prototype, "post");
  let mockedPostRequests: MockRequest[] = [];
  const mockAPIPut = vi.spyOn(APICall.prototype, "put");
  let mockedPutRequests: MockRequest[] = [];

  beforeEach(() => {
    mockAPIGet.mockImplementation(async (req) => {
      for (let i = 0; i < mockedGetRequests.length; i++) {
        const mock_req = mockedGetRequests[i];
        if (mock_req.url === req.url_path) {
          return mock_req.output;
        }
      }

      throw new Error(`${req.url_path} was not mocked`);
    });

    mockAPIPost.mockImplementation(async (req) => {
      for (let i = 0; i < mockedPostRequests.length; i++) {
        const mock_req = mockedPostRequests[i];
        if (mock_req.url === req.url_path) {
          return mock_req.output;
        }
      }

      throw new Error(`${req.url_path} was not mocked`);
    });

    mockAPIPut.mockImplementation(async (req) => {
      for (let i = 0; i < mockedPutRequests.length; i++) {
        const mock_req = mockedPutRequests[i];
        if (mock_req.url === req.url_path) {
          return mock_req.output;
        }
      }

      throw new Error(`${req.url_path} was not mocked`);
    });
  });

  afterEach(() => {
    mockedGetRequests = [];
    mockAPIGet.mockClear();

    mockedPostRequests = [];
    mockAPIPost.mockClear();

    mockedPutRequests = [];
    mockAPIPut.mockClear();

    vi.mocked(getAccessToken).mockReset();
  });

  function mockToken() {
    const token = "test-token";
    vi.mocked(getAccessToken).mockResolvedValue(token);

    return token;
  }

  function mockGet(
    input: Request,
    output: Result<unknown, ValidationErrorProp>,
  ) {
    mockedGetRequests.push({ url: input.url_path, output: output });
  }

  function mockPost(
    input: Request,
    output: Result<unknown, ValidationErrorProp>,
  ) {
    mockedPostRequests.push({ url: input.url_path, output: output });
  }

  function mockPut(
    input: Request,
    output: Result<unknown, ValidationErrorProp>,
  ) {
    mockedPutRequests.push({ url: input.url_path, output: output });
  }

  return {
    mockToken,
    mockAPIGet,
    mockGet,
    mockAPIPost,
    mockPost,
    mockAPIPut,
    mockPut,
  };
}
