from src.core.domain.utils.custom_uuid import CustomUUID, UuidAdapter

from tests.constants import UUID_LENGTH


def generate_mock_uuid(id: int) -> CustomUUID:
    """
    Generate a mock UUID based on a numeric ID.

    :param id: Numeric ID.

    :return: Mock UUID.
    """

    len_of_integer_id = len(str(id))

    if len_of_integer_id > UUID_LENGTH:
        raise ValueError(f"The number of digits in the numeric ID exceeds {UUID_LENGTH}.")

    number_of_zeros = UUID_LENGTH - len_of_integer_id
    zeros = "0" * number_of_zeros

    mock_uuid = f"{zeros}{id}"
    formatted_mock_uuid = UuidAdapter.validate(
        "-".join(
            (
                mock_uuid[:8],
                mock_uuid[8:12],
                mock_uuid[12:16],
                mock_uuid[16:20],
                mock_uuid[20:],
            ),
        )
    )

    return formatted_mock_uuid
