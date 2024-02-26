from decimal import Decimal, localcontext
from random import Random

import pytest

from polyfactory.value_generators.constrained_numbers import (
    generate_constrained_number,
    passes_pydantic_multiple_validator,
)
from polyfactory.value_generators.primitives import create_random_decimal, create_random_float


@pytest.mark.parametrize(
    ("maximum", "minimum", "multiple_of"),
    (
        (100, 2, 8),
        (-100, -187, -10),
        (7.55, 0.13, 0.0123),
        (None, 10, 3),
        (None, -10, 3),
        (13, 2, None),
        (50, None, 7),
        (-50, None, 7),
        (None, None, 4),
        (900, None, 1000),
    ),
)
def test_generate_constrained_number(maximum: float | None, minimum: float | None, multiple_of: float | None) -> None:
    value = generate_constrained_number(
        random=Random(),
        minimum=minimum,
        maximum=maximum,
        multiple_of=multiple_of,
        method=create_random_float,
    )
    if maximum is not None:
        assert value <= maximum
    if minimum is not None:
        assert value >= minimum
    if multiple_of is not None:
        assert passes_pydantic_multiple_validator(multiple_of=multiple_of, value=value)


def test_generate_constrained_number_with_overprecise_decimals() -> None:
    minimum = Decimal("1.0005")
    maximum = Decimal("2")
    multiple_of = Decimal("1.0005")

    with localcontext() as ctx:
        ctx.prec = 3

        value = generate_constrained_number(
            random=Random(),
            minimum=minimum,
            maximum=maximum,
            multiple_of=multiple_of,
            method=create_random_decimal,
        )
        if maximum is not None:
            assert value <= ctx.create_decimal(maximum)
        if minimum is not None:
            assert value >= ctx.create_decimal(minimum)
        if multiple_of is not None:
            assert passes_pydantic_multiple_validator(multiple_of=ctx.create_decimal(multiple_of), value=value)


def test_passes_pydantic_multiple_validator_handles_zero_multiplier() -> None:
    assert passes_pydantic_multiple_validator(1.0, 0)
