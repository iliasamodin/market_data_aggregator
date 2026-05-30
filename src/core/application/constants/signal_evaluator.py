from enum import StrEnum


class SignalEvaluatorMessagesEnum(StrEnum):
    """
    Trading signal evaluation execution stage messages.
    """

    LOADED_CONTEXT = "Loaded context: {count} ticker(s) ready for signal evaluation."
    GROUPED_TICKERS_BY_TIMEFRAME_AND_SCREENER = "Grouped tickers by timeframe and screener into fetch groups."
    GENERATED_TICKER_ID_AND_SNAPSHOT_MAP = "Generated map of ticker IDs and market data snapshots."
    DETECTED_NEW_TRADING_SIGNAL = "Detected new trading signal: {signal}"
    SIGNAL_EVALUATION_COMPLETED = "Signal evaluation completed with the result: {result}"
