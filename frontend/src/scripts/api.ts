const HOST = import.meta.env.VITE_BACKEND_HOST;
const PORT = import.meta.env.VITE_BACKEND_PORT;

const BASE_URL = `http://${HOST}:${PORT}/api/v1`;

class APICalls {
  base_url: string;

  public constructor(base_url: string) {
    this.base_url = base_url;
  }

  private handle_server_errors(response: Response): string {
    switch (response.status) {
      case 400:
        return response.statusText;

      case 401:
        return "You must be logged in to access this feature";

      case 403:
        return "You do not have the required permissions for this feature";

      case 404:
        return "Unable to find requested resource";

      case 422:
        return "Unprocessable data";

      case 500:
        return "An internal server error occured";

      default:
        return "An unknown error occured";
    }
  }

  public async get<TYPE>(
    url: string,
  ): Promise<[boolean, TYPE | null, string | null]> {
    let response;

    try {
      console.log("URL [GET]: " + this.base_url + url);
      response = await fetch(this.base_url + url, { credentials: "include" });
    } catch (error) {
      return [false, null, "An unknown error occured fetching data.\n" + error];
    }

    if (!response.ok) {
      const error_message = this.handle_server_errors(response);
      return [true, null, error_message];
    }

    return [true, (await response.json()) as TYPE, null];
  }

  public async post<TYPE>(
    url: string,
    payload: { [key: string]: any },
  ): Promise<[boolean, TYPE | null, string | null]> {
    let response;

    console.log(import.meta.env);

    try {
      console.log("URL [POST]: " + this.base_url + url);
      response = await fetch(this.base_url + url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
        credentials: "include",
      });
    } catch (error) {
      return [false, null, "An unknown error occured fetching data.\n" + error];
    }

    if (!response.ok) {
      const error_message = this.handle_server_errors(response);
      return [true, null, error_message];
    }

    return [true, (await response.json()) as TYPE, null];
  }

  public async put<TYPE>(
    url: string,
    payload: { [key: string]: any },
  ): Promise<[boolean, TYPE | null, string | null]> {
    let response;

    try {
      console.log("URL [PUT]: " + this.base_url + url);
      response = await fetch(this.base_url + url, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
        credentials: "include",
      });
    } catch (error) {
      return [false, null, "An unknown error occured fetching data.\n" + error];
    }

    if (!response.ok) {
      const error_message = this.handle_server_errors(response);
      return [true, null, error_message];
    }

    if (response.status != 204) {
      return [true, (await response.json()) as TYPE, null];
    }

    // Return no response when specified
    return [true, null, null];
  }

  public async delete<TYPE>(
    url: string,
  ): Promise<[boolean, TYPE | null, string | null]> {
    let response;

    try {
      console.log("URL [DELETE]: " + this.base_url + url);
      response = await fetch(this.base_url + url, {
        method: "DELETE",
        credentials: "include",
      });
    } catch (error) {
      return [false, null, "An unknown error occured fetching data.\n" + error];
    }

    if (!response.ok) {
      const error_message = this.handle_server_errors(response);
      return [true, null, error_message];
    }

    if (response.status != 204) {
      return [true, (await response.json()) as TYPE, null];
    }

    // Return no response when specified
    return [true, null, null];
  }
}

export default new APICalls(BASE_URL);
