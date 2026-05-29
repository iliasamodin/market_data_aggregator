from collections import defaultdict
from collections.abc import Collection
from typing import Self

from pydantic import BaseModel, Field

from src.core.domain.entities.group import GroupEntity
from src.core.domain.entities.ticker import TickerEntity
from src.core.domain.utils.custom_uuid import CustomUUID


class BidirectionalTickerGroupMapDTO(BaseModel):
    """
    Bidirectional map of ticker's IDs and group's IDs.
    """

    ticker_ids_and_group_ids: dict[CustomUUID, list[CustomUUID]] = Field(default_factory=lambda: defaultdict(list))
    group_ids_and_ticker_ids: dict[CustomUUID, list[CustomUUID]] = Field(default_factory=lambda: defaultdict(list))

    @classmethod
    def init_map(cls, tickers: Collection[TickerEntity]) -> Self:
        """
        Initializes a bidirectional map of ticker's IDs and group's IDs.

        :param tickers: Collection of tickers.

        :return: Bidirectional map.
        """

        bidirectional_map = cls()

        for ticker in tickers:
            for config in ticker.calculation_configs:
                bidirectional_map.ticker_ids_and_group_ids[ticker.id].append(config.group_id)
                bidirectional_map.group_ids_and_ticker_ids[config.group_id].append(ticker.id)

        return bidirectional_map


class BidirectionalGroupAlgoConfigMapDTO(BaseModel):
    """
    Bidirectional map of group's IDs and algorithm configuration's IDs.
    """

    group_ids_and_algo_config_ids: dict[CustomUUID, list[CustomUUID]] = Field(default_factory=lambda: defaultdict(list))
    algo_config_ids_and_group_ids: dict[CustomUUID, list[CustomUUID]] = Field(default_factory=lambda: defaultdict(list))

    @classmethod
    def init_map(cls, groups: Collection[GroupEntity]) -> Self:
        """
        Initializes a bidirectional map of group's IDs
        and algorithm configuration's IDs.

        :param groups: Collection of groups.

        :return: Bidirectional map.
        """

        bidirectional_map = cls()

        for group in groups:
            for algorithm_config_id in group.algorithm_config_ids:
                bidirectional_map.group_ids_and_algo_config_ids[group.id].append(algorithm_config_id)
                bidirectional_map.algo_config_ids_and_group_ids[algorithm_config_id].append(group.id)

        return bidirectional_map
