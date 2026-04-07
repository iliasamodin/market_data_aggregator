from pydantic import BaseModel, Field, ConfigDict


class IndicatorsSnapshotVO(BaseModel):
    """
    Current values of indicators for ticker operational data.
    """

    # RSI
    rsi: float | None = Field(default=None, alias="RSI")
    previous_rsi: float | None = Field(default=None, alias="RSI[1]")

    # ADX
    adx: float | None = Field(default=None, alias="ADX")
    adx_pos_di: float | None = Field(default=None, alias="ADX+DI")
    adx_neg_di: float | None = Field(default=None, alias="ADX-DI")
    previous_adx_pos_di: float | None = Field(default=None, alias="ADX+DI[1]")
    previous_adx_neg_di: float | None = Field(default=None, alias="ADX-DI[1]")

    # MACD
    macd: float | None = Field(default=None, alias="MACD.macd")
    macd_signal: float | None = Field(default=None, alias="MACD.signal")

    # MA
    sma20: float | None = Field(default=None, alias="SMA20")
    sma50: float | None = Field(default=None, alias="SMA50")
    sma200: float | None = Field(default=None, alias="SMA200")

    model_config = ConfigDict(
        populate_by_name=True,
    )
