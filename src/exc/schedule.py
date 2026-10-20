from fastapi import HTTPException, status


HTTP_EXC_BACKUP_SCHEDULE_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="Backup schedule does not exist"
)
