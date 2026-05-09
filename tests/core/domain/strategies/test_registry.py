import pytest
import logging

from src.core.domain.constants.algorithm import AlgorithmEnum
from src.core.domain.strategies.registry import STRATEGY_MAP


@pytest.mark.unit
def test_all_algorithms_are_registered_in_strategy_map():
    """
    Architecture test.
    Ensures that when an algorithm is added to <AlgorithmEnum>,
    the corresponding strategy function is added to <STRATEGY_MAP>.
    """

    logging.log(
        level=logging.INFO,
        msg="Checking that all algorithms are registered in <STRATEGY_MAP>.",
    )

    missing_algorithms = [algorithm.name for algorithm in AlgorithmEnum if algorithm not in STRATEGY_MAP]

    assert not missing_algorithms, f"Missing algorithms: {missing_algorithms}"
