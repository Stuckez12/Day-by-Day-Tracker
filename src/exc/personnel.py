from fastapi import HTTPException, status


HTTP_EXC_PERSONNEL_DOES_NOT_EXIST = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="Personnel does not exist"
)
