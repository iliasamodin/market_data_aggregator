from src.core.domain.constants.algorithm import AlgorithmEnum
from src.core.domain.strategies.adx import (
    adx_consolidation_stage_transition,
    adx_extreme_trend_reached,
    adx_pos_di_growth,
    adx_pos_di_decline,
    adx_neg_di_growth,
    adx_neg_di_decline,
    adx_di_bullish_crossover,
    adx_di_bearish_crossover,
)
from src.core.domain.strategies.envelope import (
    envelope_lower_boundary_breakout,
    envelope_upper_boundary_breakout,
)
from src.core.domain.strategies.macd import (
    macd_signal_line_bullish_crossover,
    macd_signal_line_bearish_crossover,
)
from src.core.domain.strategies.rsi import (
    rsi_oversold_reached,
    rsi_overbought_reached,
    rsi_growth,
    rsi_decline,
)
from src.core.domain.types import StrategyMapType

STRATEGY_MAP: StrategyMapType = {
    AlgorithmEnum.ADX_CONSOLIDATION_STAGE_TRANSITION: adx_consolidation_stage_transition,
    AlgorithmEnum.ADX_EXTREME_TREND_REACHED: adx_extreme_trend_reached,
    AlgorithmEnum.ADX_POS_DI_GROWTH: adx_pos_di_growth,
    AlgorithmEnum.ADX_POS_DI_DECLINE: adx_pos_di_decline,
    AlgorithmEnum.ADX_NEG_DI_GROWTH: adx_neg_di_growth,
    AlgorithmEnum.ADX_NEG_DI_DECLINE: adx_neg_di_decline,
    AlgorithmEnum.ADX_DI_BULLISH_CROSSOVER: adx_di_bullish_crossover,
    AlgorithmEnum.ADX_DI_BEARISH_CROSSOVER: adx_di_bearish_crossover,
    AlgorithmEnum.ENVELOPE_LOWER_BOUNDARY_BREAKOUT: envelope_lower_boundary_breakout,
    AlgorithmEnum.ENVELOPE_UPPER_BOUNDARY_BREAKOUT: envelope_upper_boundary_breakout,
    AlgorithmEnum.MACD_SIGNAL_LINE_BULLISH_CROSSOVER: macd_signal_line_bullish_crossover,
    AlgorithmEnum.MACD_SIGNAL_LINE_BEARISH_CROSSOVER: macd_signal_line_bearish_crossover,
    AlgorithmEnum.RSI_OVERSOLD_REACHED: rsi_oversold_reached,
    AlgorithmEnum.RSI_OVERBOUGHT_REACHED: rsi_overbought_reached,
    AlgorithmEnum.RSI_GROWTH: rsi_growth,
    AlgorithmEnum.RSI_DECLINE: rsi_decline,
}
