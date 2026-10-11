from fastapi import Request


def client_ipaddress(request: Request) -> str:
    if "x-forwarded-for" in request.headers:
        return request.headers["x-forwarded-for"]

    if not request.client or not request.client.host:
        return "127.0.0.1"

    return request.client.host
