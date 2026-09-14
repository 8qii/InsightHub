from pydantic import BaseModel, ConfigDict


class DiscountViolations(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_violations: int
    unapproved_violations: int
