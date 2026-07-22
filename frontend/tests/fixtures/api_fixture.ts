import { afterAll, beforeEach, beforeAll, vi } from "vitest";
import { APICall, Request, RequestBody } from "@/lib/queries/base";
import { Result, ValidationErrorProp } from "@/lib/interfaces/common";

const apiCall = new APICall("");

interface MockGetRequest {
  url: string;
  output: Result<unknown, ValidationErrorProp>;
}

interface MockPostRequest {
  url: string;
  output: Result<unknown, ValidationErrorProp>;
}

export function useAPIFixture() {
  const mockAPIGet = vi.spyOn(APICall.prototype, "get");
  let mockedGetRequests: MockGetRequest[] = [];
  const mockAPIPost = vi.spyOn(APICall.prototype, "post");
  let mockedPostRequests: MockPostRequest[] = [];

  beforeAll(() => {
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
  });

  afterAll(() => {
    mockedGetRequests = [];
    mockedPostRequests = [];
    mockAPIGet.mockRestore();
    mockAPIPost.mockRestore();
  });

  beforeEach(() => {
    mockedGetRequests = [];
    mockedPostRequests = [];
    mockAPIGet.mockClear();
    mockAPIPost.mockClear();
  });

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

  return {
    mockAPIGet,
    mockGet,
    mockAPIPost,
    mockPost,
  };
}
