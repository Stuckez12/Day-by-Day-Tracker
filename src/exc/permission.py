from fastapi import HTTPException, status


HTTP_EXC_NOT_AN_ADMIN = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="You must be an admin to access this resource",
)
