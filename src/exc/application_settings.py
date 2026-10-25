from fastapi import HTTPException, status


HTTP_EXC_APP_SETTINGS_NO_RESTORE_BACKUP_ID = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="No backup"
)
HTTP_EXC_APP_SEETINGS_UNABLE_TO_FETCH_MODIFY_CONFIG = HTTPException(
    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
    detail="Unable to retrieve or modify application config",
)
