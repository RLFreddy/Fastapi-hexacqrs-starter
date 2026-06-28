from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ValidationErrorItem(BaseModel):
    loc: list[str] = Field(
        ...,
        examples=[["body", "email"]],
        description="Location of the field that failed validation",
    )
    msg: str = Field(
        ...,
        examples=[
            "value is not a valid email address: The email address is not valid. It must have exactly one @-sign."
        ],
        description="Human-readable error message",
    )
    type: str = Field(
        ...,
        examples=["value_error"],
        description="Error type identifier",
    )
    input: Any = Field(
        default=None,
        examples=["not-an-email"],
        description="The input value that failed validation",
    )
    ctx: dict | None = Field(
        default=None,
        examples=[None],
        description="Additional context about the error",
    )


class ValidationErrorResponse(BaseModel):
    detail: list[ValidationErrorItem]
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "detail": [
                        {
                            "loc": ["body", "email"],
                            "msg": "value is not a valid email address: The email address is not valid. It must have exactly one @-sign.",  # noqa: E501
                            "type": "value_error",
                            "input": "not-an-email",
                        }
                    ]
                },
                {
                    "detail": [
                        {
                            "loc": ["body", "password"],
                            "msg": "String should have at least 6 characters",
                            "type": "string_too_short",
                            "input": "abc",
                            "ctx": {"min_length": 6},
                        }
                    ]
                },
                {
                    "detail": [
                        {
                            "loc": ["body", "password"],
                            "msg": "Field required",
                            "type": "missing",
                            "input": {"email": "user@example.com"},
                        }
                    ]
                },
            ]
        }
    )
