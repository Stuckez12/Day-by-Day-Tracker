from datetime import date
from pydantic import BaseModel, model_validator


class DateRequest(BaseModel):
    date: date


class DateRangeRequest(BaseModel):
    min_date: date
    max_date: date

    @model_validator(mode="after")
    def validate_date_range(self):
        if self.min_date > self.max_date:
            raise ValueError("Date range must be valid")

        return self
