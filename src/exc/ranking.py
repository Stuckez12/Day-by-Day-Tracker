from fastapi import HTTPException, status


HTTP_EXC_RANKING_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Ranked date not found",
)
HTTP_EXC_NO_RANK_PROVIDED = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="A rank must be provided",
)
HTTP_EXC_INVALID_RANK_VALUE = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Ranking must be between 0 and 10",
)
HTTP_EXC_RANK_OLDER_THAN_TWO_WEEKS = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="You cannot modify a ranked day more than two weeks old",
)
