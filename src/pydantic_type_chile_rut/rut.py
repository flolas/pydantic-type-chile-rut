"""Chilean RUT validation and formatting for Pydantic."""

import re
from typing import Any

from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema


def _compute_dv(body: str) -> str:
    """
    Compute Chilean RUT check digit using modulo 11.
    Returns '0'-'9' or 'K'.
    """
    weights = [2, 3, 4, 5, 6, 7]
    total = 0
    for i, ch in enumerate(reversed(body)):
        total += int(ch) * weights[i % len(weights)]
    mod = 11 - (total % 11)
    if mod == 11:
        return "0"
    if mod == 10:
        return "K"
    return str(mod)


def _parse_and_validate_rut(value: Any) -> tuple[str, str]:
    """
    Normalize and validate a RUT-like input.
    Accepts with/without dots and hyphen, lowercase/uppercase 'k'.
    Returns (body_without_leading_zeros, dv_uppercase).
    """
    s = str(value).strip().upper()
    s = s.replace("–", "-").replace("—", "-").replace("−", "-")
    s = s.replace(".", "").replace(" ", "")
    compact = re.sub(r"[^0-9K]", "", s)
    if (
        len(compact) < 2
        or not compact[:-1].isdigit()
        or compact[-1] not in "0123456789K"
    ):
        raise ValueError("Invalid RUT format")

    body = compact[:-1].lstrip("0") or "0"
    dv = compact[-1]

    if not (1 <= len(body) <= 9):
        raise ValueError("Invalid RUT length")

    if _compute_dv(body) != dv:
        raise ValueError("Invalid RUT check digit")

    return body, dv


class RutNumber(str):
    """
    Pydantic custom type for Chilean RUT, validated and normalized to '########-X' (uppercase DV).
    Accessible components:
        .number -> int (body without leading zeros)
        .dv     -> str ('0'-'9' or 'K')
    Formatted with dots (thousands) and hyphen:
        .with_dots()  -> '12.345.678-5'
        .formatted    -> same as with_dots()
    The stored str value is normalized WITHOUT dots: e.g., '12345678-5'
    """

    __slots__ = ("number", "dv")

    # Type hints for mypy
    number: int
    dv: str

    def __new__(cls, number: int, dv: str) -> "RutNumber":
        obj = super().__new__(cls, f"{int(number)}-{dv}")
        obj.number = int(number)
        obj.dv = dv
        return obj

    def __repr__(self) -> str:
        return f"RutNumber(number={self.number}, dv='{self.dv}')"

    def with_dots(self) -> str:
        """Return the RUT formatted with thousands dots and hyphen, e.g., '12.345.678-5'."""
        body_with_dots = f"{self.number:,}".replace(",", ".")
        return f"{body_with_dots}-{self.dv}"

    @property
    def formatted(self) -> str:
        """Alias of .with_dots()"""
        return self.with_dots()

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        def validate(value: Any) -> "RutNumber":
            body, dv = _parse_and_validate_rut(value)
            return cls(int(body), dv)

        return core_schema.no_info_plain_validator_function(validate)
