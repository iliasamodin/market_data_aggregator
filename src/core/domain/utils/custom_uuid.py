from __future__ import annotations

from typing import Annotated, Any

from pydantic_core import core_schema
from uuid_utils import UUID


class UuidAdapter:
    """
    Adapter <uuid_utils.UUID> for Pydantic models.
    """

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: Any,
    ) -> core_schema.CoreSchema:
        """
        Get custom pydantic core schema.

        :param source_type: Source type.
        :param handler: Handler.

        :return: Custom pydantic core schema.
        """

        schema = core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.any_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x),
                info_arg=False,
                return_schema=core_schema.str_schema(),
            ),
        )

        return schema

    @classmethod
    def validate(cls, value: Any) -> UUID:
        """
        Validate UUID.

        :param value: Value to validate.

        :return: UUID.
        """

        try:
            uuid_value = UUID(str(value))

        except Exception:
            raise ValueError("Invalid input data to UUID.")

        return uuid_value


CustomUUID = Annotated[
    UUID,
    UuidAdapter,
]
