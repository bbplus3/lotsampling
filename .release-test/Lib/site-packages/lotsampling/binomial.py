"""Binomial sampling plans for continuous or large lots."""

import numpy as np

from .models import SamplingPlanResult


def calculate_binomial_sample_size(
    max_nonconformance: float,
    consumer_risk: float,
) -> int:
    """Calculate the required sample size for a zero-acceptance plan.

    This function assumes the lot is modeled using a binomial distribution
    and that the acceptance number is zero.

    Parameters
    ----------
    max_nonconformance:
        The nonconformance rate the plan should protect against.

        Example:
        Use ``0.20`` for a 20% nonconformance rate.

    consumer_risk:
        The maximum probability of accepting a lot at the specified
        nonconformance rate.

        Example:
        Use ``0.05`` for a 5% consumer risk.

    Returns
    -------
    int
        The minimum required sample size.

    Raises
    ------
    TypeError
        If either input is not numeric.

    ValueError
        If either probability is not between 0 and 1.

    Examples
    --------
    >>> calculate_binomial_sample_size(0.20, 0.05)
    14
    """

    max_nonconformance = _validate_probability(
        max_nonconformance,
        name="max_nonconformance",
        hint="Use a decimal such as 0.20 for 20%.",
    )

    consumer_risk = _validate_probability(
        consumer_risk,
        name="consumer_risk",
        hint="Use a decimal such as 0.05 for 5%.",
    )

    return int(
        np.ceil(
            np.log(consumer_risk)
            / np.log(1.0 - max_nonconformance)
        )
    )


def evaluate_binomial_plan(
    sample_size: int,
    lot_size: int,
    max_nonconformance: float = 0.20,
    points: int = 201,
) -> SamplingPlanResult:
    """Evaluate a zero-acceptance binomial sampling plan.

    Parameters
    ----------
    sample_size:
        Number of units inspected from each lot.

    lot_size:
        Total number of units in the lot.

    max_nonconformance:
        Highest nonconformance rate shown in the calculated curves.

        The default is ``0.20``, representing 20%.

    points:
        Number of values evaluated between zero and
        ``max_nonconformance``.

        The default is 201.

    Returns
    -------
    SamplingPlanResult
        Named sampling-plan metrics and curve data.

    Raises
    ------
    TypeError
        If sample size, lot size, or points are not integers.

    ValueError
        If sample size or lot size is invalid.

    Examples
    --------
    >>> result = evaluate_binomial_plan(30, 500)
    >>> round(result.aoql, 4)
    0.0113
    """

    sample_size = _validate_positive_integer(
        sample_size,
        name="sample_size",
    )

    lot_size = _validate_positive_integer(
        lot_size,
        name="lot_size",
    )

    points = _validate_positive_integer(
        points,
        name="points",
    )

    if sample_size > lot_size:
        raise ValueError(
            "sample_size cannot be greater than lot_size. "
            f"You entered sample_size={sample_size} and "
            f"lot_size={lot_size}. Reduce the sample size or increase "
            "the lot size."
        )

    if points < 2:
        raise ValueError(
            "points must be at least 2 so a curve can be calculated."
        )

    max_nonconformance = _validate_probability(
        max_nonconformance,
        name="max_nonconformance",
        allow_one=True,
        hint="Use a decimal such as 0.20 for 20%.",
    )

    nonconformance_rates = np.linspace(
        0.0,
        max_nonconformance,
        points,
        dtype=np.float64,
    )

    # Zero-acceptance binomial plan:
    # P(acceptance) = P(X = 0) = (1 - p) ** n
    acceptance_probabilities = (
        1.0 - nonconformance_rates
    ) ** sample_size

    average_fraction_inspected = (
        1.0
        - (1.0 - sample_size / lot_size)
        * acceptance_probabilities
    )

    average_outgoing_quality = (
        nonconformance_rates
        * (1.0 - average_fraction_inspected)
    )

    aoql = (
        (1.0 - sample_size / lot_size)
        / (sample_size + 1)
        * (sample_size / (sample_size + 1)) ** sample_size
    )

    equal_risk_point = 1.0 - 0.50 ** (1.0 / sample_size)
    lot_tolerance = 1.0 - 0.10 ** (1.0 / sample_size)
    rejectable_quality_level = (
        1.0 - 0.05 ** (1.0 / sample_size)
    )

    return SamplingPlanResult(
        nonconformance_rates=nonconformance_rates,
        acceptance_probabilities=acceptance_probabilities,
        average_fraction_inspected=average_fraction_inspected,
        average_outgoing_quality=average_outgoing_quality,
        aoql=float(aoql),
        equal_risk_point=float(equal_risk_point),
        lot_tolerance=float(lot_tolerance),
        rejectable_quality_level=float(
            rejectable_quality_level
        ),
    )


def _validate_probability(
    value: float,
    *,
    name: str,
    hint: str,
    allow_one: bool = False,
) -> float:
    """Validate a probability supplied to a public function."""

    if isinstance(value, bool) or not isinstance(
        value,
        (int, float, np.integer, np.floating),
    ):
        raise TypeError(
            f"{name} must be a number. {hint}"
        )

    value = float(value)

    upper_bound_is_valid = value <= 1 if allow_one else value < 1

    if value <= 0 or not upper_bound_is_valid:
        interval = "(0, 1]" if allow_one else "(0, 1)"

        raise ValueError(
            f"{name} must be within {interval}. "
            f"You entered {value}. {hint}"
        )

    return value


def _validate_positive_integer(
    value: int,
    *,
    name: str,
) -> int:
    """Validate a positive integer supplied to a public function."""

    if isinstance(value, bool) or not isinstance(
        value,
        (int, np.integer),
    ):
        raise TypeError(
            f"{name} must be a whole number. "
            f"Example: {name}=30."
        )

    value = int(value)

    if value <= 0:
        raise ValueError(
            f"{name} must be greater than zero. "
            f"You entered {value}."
        )

    return value


# Backward-compatible aliases.
findn = calculate_binomial_sample_size
lotsameval = evaluate_binomial_plan