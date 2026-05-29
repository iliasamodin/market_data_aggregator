import json

from src.adapters.primary.constants.shared import DETAIL, UnsuccessfulResponseDetailEnum


def prepare_response_detail(detail: str | None = None) -> str:
    """
    Prepare a response detail string.

    :param detail: Detail to be included in the response.

    :return: Detail string.
    """

    resulting_detail = {DETAIL: UnsuccessfulResponseDetailEnum.INTERNAL_SERVER_ERROR.value}
    if detail is not None:
        resulting_detail[DETAIL] = detail

    resulting_detail = json.dumps(resulting_detail)

    return resulting_detail
