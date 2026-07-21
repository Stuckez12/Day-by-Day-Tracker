import { Result, ValidationErrorProp } from "@/lib/interfaces/common";

export interface Request {
  url_path: string;
  token?: string;
}

interface RequestBody extends Request {
  body: Record<string, unknown>;
}

enum RequestType {
  GET,
  POST,
  PUT,
  PATCH,
  DELETE,
}

export class APICall {
  base_url: string;

  public constructor(base_url: string) {
    this.base_url = base_url;
  }

  private define_headers(req: Request, req_type: RequestType) {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };

    if (req.token !== null) {
      headers["Authorization"] = `Bearer ${req.token}`;
    }

    return headers;
  }

  private async handle_response<T>(
    response: Response,
  ): Promise<Result<T, ValidationErrorProp>> {
    let body = null;

    try {
      if (response.status !== 204) {
        body = await response.json();
      }
    } catch {
      body = null;
    }

    if (response.ok) {
      return { ok: true, data: body };
    }

    return {
      ok: false,
      error: {
        api_response: true,
        error_count: 1,
        errors: { api: body?.detail ?? "Unknown API error" },
      },
    };
  }

  public async get<T>(req: Request) {
    const headers = this.define_headers(req, RequestType.GET);
    const response = await fetch(`${this.base_url}/api${req.url_path}`, {
      method: "GET",
      headers: headers,
    });

    return this.handle_response<T>(response);
  }

  public async post<T>(req: RequestBody) {
    const headers = this.define_headers(req, RequestType.POST);
    const response = await fetch(`${this.base_url}/api${req.url_path}`, {
      method: "POST",
      body: JSON.stringify(req.body),
      headers: headers,
    });

    return this.handle_response<T>(response);
  }

  public async put<T>(req: RequestBody) {
    const headers = this.define_headers(req, RequestType.PUT);
    const response = await fetch(`${this.base_url}/api${req.url_path}`, {
      method: "PUT",
      body: JSON.stringify(req.body),
      headers: headers,
    });

    return this.handle_response<T>(response);
  }

  public async patch<T>(req: RequestBody) {
    const headers = this.define_headers(req, RequestType.PATCH);
    const response = await fetch(`${this.base_url}/api${req.url_path}`, {
      method: "PATCH",
      body: JSON.stringify(req.body),
      headers: headers,
    });

    return this.handle_response<T>(response);
  }

  public async delete<T>(req: Request) {
    const headers = this.define_headers(req, RequestType.DELETE);
    const response = await fetch(`${this.base_url}/api${req.url_path}`, {
      method: "DELETE",
      headers: headers,
    });

    return this.handle_response<T>(response);
  }
}

export const MustBeLoggedIn: Result<never, ValidationErrorProp> = {
  ok: false,
  error: {
    api_response: false,
    error_count: 1,
    errors: { account: ["You must be logged in to perform this action"] },
  },
};
