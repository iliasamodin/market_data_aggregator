from pydantic import BaseModel


class SignalEvaluationResultDTO(BaseModel):
    """
    Result of evaluating signals.
    """

    processed_configs_count: int = 0
    created_signals_count: int = 0
    sent_signals_count: int = 0
