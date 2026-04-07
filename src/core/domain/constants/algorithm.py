from enum import StrEnum


class AlgorithmEnum(StrEnum):
    """
    Trading algorithm.
    """

    ADX_CONSOLIDATION_STAGE_TRANSITION = "adx_consolidation_stage_transition"
    ADX_EXTREME_TREND_REACHED = "adx_extreme_trend_reached"
    ADX_POS_DI_GROWTH = "adx_pos_di_growth"
    ADX_POS_DI_DECLINE = "adx_pos_di_decline"
    ADX_NEG_DI_GROWTH = "adx_neg_di_growth"
    ADX_NEG_DI_DECLINE = "adx_neg_di_decline"
    ADX_DI_BULLISH_CROSSOVER = "adx_di_bullish_crossover"
    ADX_DI_BEARISH_CROSSOVER = "adx_di_bearish_crossover"
    ENVELOPE_LOWER_BOUNDARY_BREAKOUT = "envelope_lower_boundary_breakout"
    ENVELOPE_UPPER_BOUNDARY_BREAKOUT = "envelope_upper_boundary_breakout"
    MACD_SIGNAL_LINE_BULLISH_CROSSOVER = "macd_signal_line_bullish_crossover"
    MACD_SIGNAL_LINE_BEARISH_CROSSOVER = "macd_signal_line_bearish_crossover"
    RSI_OVERSOLD_REACHED = "rsi_oversold_reached"
    RSI_OVERBOUGHT_REACHED = "rsi_overbought_reached"
    RSI_GROWTH = "rsi_growth"
    RSI_DECLINE = "rsi_decline"
