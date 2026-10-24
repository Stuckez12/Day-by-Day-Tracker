from fastapi import HTTPException, status


HTTP_EXC_BACKUP_SCHEDULE_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="Backup schedule does not exist"
)
HTTP_EXC_ERROR_CANCELLING_QUEUED_TASK = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail="Unable to cancel scheduled backup",
)
HTTP_EXC_BACKUP_SCHEDULE_ALREADY_EXISTS = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="A backup schedule already exists for this date",
)
