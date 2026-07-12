import { ValidationErrorProp } from "@/lib/interfaces/common";

interface Request {
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
    let headers: Record<string, string> = {
      "Content-Type": "application/json",
    };

    if (req.token !== null) {
      headers["Authorisation"] = `Bearer ${req.token}`;
    }

    return headers;
  }

  public async get(req: Request) {
    const headers = this.define_headers(req, RequestType.GET);
    return await fetch(req.url_path, {
      method: "GET",
      headers: headers,
    });
  }

  public async post(req: RequestBody) {
    const headers = this.define_headers(req, RequestType.POST);
    return await fetch(req.url_path, {
      method: "POST",
      body: JSON.stringify(req.body),
      headers: headers,
    });
  }

  public async put(req: RequestBody) {
    const headers = this.define_headers(req, RequestType.PUT);
    return await fetch(req.url_path, {
      method: "PUT",
      body: JSON.stringify(req.body),
      headers: headers,
    });
  }

  public async patch(req: RequestBody) {
    const headers = this.define_headers(req, RequestType.PATCH);
    return await fetch(req.url_path, {
      method: "PATCH",
      body: JSON.stringify(req.body),
      headers: headers,
    });
  }

  public async delete(req: Request) {
    const headers = this.define_headers(req, RequestType.DELETE);
    return await fetch(req.url_path, {
      method: "DELETE",
      headers: headers,
    });
  }
}

export const MustBeLoggedIn = {
  api_response: false,
  error_count: 1,
  errors: { account: ["You must be logged in to perform this action"] },
} as ValidationErrorProp;
