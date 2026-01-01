const BASE_URL = "http://localhost:8000/api/v1"


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

    public async get<TYPE>(url: string): Promise<[boolean, TYPE | null, string | null]> {
        let response;

        try {
            console.log("URL: "+  this.base_url + url)
            response = await fetch(this.base_url + url);
        } catch (error) {
            return [false, null, "An unknown error occured fetching data.\n" + error]
        }

        if (!response.ok){
            const error_message = this.handle_server_errors(response);
            return [true, null, error_message];
        }

        return [true, (await response.json()) as TYPE, null];
    }
}

export default new APICalls(BASE_URL);
