from fastapi import HTTPException, status


HTTP_EXC_TASK_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="Task does not exist"
)
HTTP_EXC_INVALID_TASK_MINIMUM_RETRY_INPUT = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Minimum retries must be a positive number",
)
HTTP_EXC_INVALID_TASK_RETRY_RANGE = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Minimum retries is larger than maximum retries",
)
HTTP_EXC_INVALID_TASK_DURATION_INPUT = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Task duration must be a positive number",
)
HTTP_EXC_INVALID_TASK_DATE_RANGE = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Started at time is larger than ended at time",
)
