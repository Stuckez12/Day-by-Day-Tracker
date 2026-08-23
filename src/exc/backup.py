from fastapi import HTTPException, status


HTTP_EXC_BACKUP_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="Backup does not exist"
)
HTTP_EXC_NO_BACKUP_METADATA = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Backup does not have the required metadata",
)
HTTP_EXC_NO_VALID_BACKUP_ID = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="You must provide either a backup id or celery task id",
)
HTTP_EXC_NO_BACKUP_FILENAME = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="File uploaded does not have a file name attached. Cancelled file upload",
)
