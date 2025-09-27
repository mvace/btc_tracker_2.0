from decimal import Decimal
from pydantic import BaseModel, Field
from datetime import datetime
from pydantic_core.core_schema import ValidationInfo
from pydantic import BaseModel, model_validator
from typing import Self


class PortfolioCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    goal_in_usd: Decimal = Decimal("0.0")


class PortfolioRead(BaseModel):
    id: int
    name: str
    goal_in_usd: Decimal = Decimal("0.0")
    model_config = {"from_attributes": True}


class PortfolioReadWithMetrics(PortfolioRead):
    # Fields from the database
    initial_value_usd: Decimal = Decimal("0.0")
    total_btc_amount: Decimal = Decimal("0.0")
    average_price_usd: Decimal = Decimal("0.0")

    # Fields that will be computed by the validator
    current_value_usd: Decimal | None = None
    net_result: Decimal | None = None
    roi: Decimal | None = None  # Return on Investment

    model_config = {"from_attributes": True}

    @model_validator(mode="after")
    def calculate_metrics(self, info: ValidationInfo) -> Self:
        # IDEMPOTENCY CHECK: If fields are already calculated, we're in the
        # second validation pass by FastAPI. Do nothing.
        if self.current_value_usd is not None:
            return self

        # --- The rest of your existing logic for the first pass ---
        current_price = info.context.get("current_price")
        if current_price is None:
            raise ValueError(
                "`current_price` must be provided in the validation context."
            )
        # Calculate the current total value
        # Note: Your original calculation was based on initial_value_usd,
        # it should likely be based on the total_btc_amount held. I've corrected this.
        self.current_value_usd = self.total_btc_amount * current_price

        # Calculate net result and ROI, handling division by zero
        if self.initial_value_usd > 0:
            self.net_result = self.current_value_usd - self.initial_value_usd
            self.roi = self.net_result / self.initial_value_usd
        else:
            # If there was no initial investment, results are zero
            self.net_result = Decimal("0.0")
            self.roi = Decimal("0.0")

        return self
