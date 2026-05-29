from enum import StrEnum


class ScreenerEnum(StrEnum):
    """
    Trading ticker screener.
    """

    CRYPTO = "crypto"
    FOREX = "forex"
    CFD = "cfd"
    STOCKS_US = "america"
    STOCKS_UK = "uk"
    STOCKS_JP = "japan"
    STOCKS_RU = "russia"
