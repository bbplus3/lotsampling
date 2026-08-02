"""Hypergeometric sampling plans for finite isolated lots."""

import numpy as np
from scipy.stats import hypergeom

from .models import SamplingPlanResult


def calculate_hypergeometric_sample_size(
    lot_size: int,
    defect_count: int,
    consumer_risk: float,
) -> int:
    """Calculate a sample size for a finite zero-acceptance plan.

    Parameters
    ----------
    lot_size:
        Total number of units in the isolated lot.

    defect_count:
        Number of nonconforming units representing the condition
        the plan should protect against.

        Example:
        For a lot of 50 units and a 10% nonconformance condition,
        use ``defect_count=5``.

    consumer_risk:
        Maximum probability of accepting the lot when it contains
        ``defect_count`` nonconforming units.

        Example:
        Use ``0.10`` for a 10% consumer risk.

    Returns
    -------
    int
        The smallest sample size that satisfies the consumer-risk limit.

    Examples
    --------
    >>> calculate_hypergeometric_sample_size(50, 5, 0.10)
    18
    """

    lot_size = _validate_positive_integer(
        lot_size,
        name="lot_size",
    )

    defect_count = _validate_positive_integer(
        defect_count,
        name="defect_count",
    )

    consumer_risk = _validate_probability(
        consumer_risk,
        name="consumer_risk",
    )

    if defect_count > lot_size:
        raise ValueError(
            "defect_count cannot be greater than lot_size. "
            f"You entered defect_count={defect_count} and "
            f"lot_size={lot_size}."
        )

    for sample_size in range(1, lot_size + 1):
        probability_of_acceptance = hypergeom.cdf(
            0,
            lot_size,
            defect_count,
            sample_size,
        )

        if probability_of_acceptance <= consumer_risk:
            return sample_size

    raise ValueError(
        "No sample size satisfies the requested consumer risk. "
        "Review the lot size, defect count, and risk inputs."
    )


def evaluate_hypergeometric_plan(
    sample_size: int,
    lot_size: int,
) -> SamplingPlanResult:
    """Evaluate a finite zero-acceptance sampling plan.

    Parameters
    ----------
    sample_size:
        Number of units inspected from the isolated lot.

    lot_size:
        Total number of units in the isolated lot.

    Returns
    -------
    SamplingPlanResult
        Named sampling-plan metrics and curve data.

    Examples
    --------
    >>> result = evaluate_hypergeometric_plan(10, 50)
    >>> result.aoql > 0
    True
    """

    sample_size = _validate_positive_integer(
        sample_size,
        name="sample_size",
    )

    lot_size = _validate_positive_integer(
        lot_size,
        name="lot_size",
    )

    if sample_size > lot_size:
        raise ValueError(
            "sample_size cannot be greater than lot_size. "
            f"You entered sample_size={sample_size} and "
            f"lot_size={lot_size}."
        )

    defect_counts = np.arange(
        0,
        lot_size + 1,
        dtype=np.int64,
    )

    nonconformance_rates = (
        defect_counts.astype(np.float64) / lot_size
    )

    acceptance_probabilities = hypergeom.cdf(
        0,
        lot_size,
        defect_counts,
        sample_size,
    ).astype(np.float64)

    average_fraction_inspected = (
        1.0
        - (1.0 - sample_size / lot_size)
        * acceptance_probabilities
    )

    average_outgoing_quality = (
        nonconformance_rates
        * (1.0 - average_fraction_inspected)
    )

    aoql = float(np.max(average_outgoing_quality))

    equal_risk_point = _find_threshold_rate(
        nonconformance_rates,
        acceptance_probabilities,
        threshold=0.50,
    )

    lot_tolerance = _find_threshold_rate(
        nonconformance_rates,
        acceptance_probabilities,
        threshold=0.10,
    )

    rejectable_quality_level = _find_threshold_rate(
        nonconformance_rates,
        acceptance_probabilities,
        threshold=0.05,
    )

    return SamplingPlanResult(
        nonconformance_rates=nonconformance_rates,
        acceptance_probabilities=acceptance_probabilities,
        average_fraction_inspected=average_fraction_inspected,
        average_outgoing_quality=average_outgoing_quality,
        aoql=aoql,
        equal_risk_point=equal_risk_point,
        lot_tolerance=lot_tolerance,
        rejectable_quality_level=rejectable_quality_level,
    )


def _find_threshold_rate(
    nonconformance_rates: np.ndarray,
    acceptance_probabilities: np.ndarray,
    *,
    threshold: float,
) -> float:
    """Find the first rate at or below an acceptance threshold."""

    matching_indices = np.flatnonzero(
        acceptance_probabilities <= threshold
    )

    if matching_indices.size == 0:
        return float("nan")

    return float(
        nonconformance_rates[matching_indices[0]]
    )


def _validate_positive_integer(
    value: int,
    *,
    name: str,
) -> int:
    """Validate a positive integer."""

    if isinstance(value, bool) or not isinstance(
        value,
        (int, np.integer),
    ):
        raise TypeError(
            f"{name} must be a whole number. "
            f"Example: {name}=50."
        )

    value = int(value)

    if value <= 0:
        raise ValueError(
            f"{name} must be greater than zero. "
            f"You entered {value}."
        )

    return value


def _validate_probability(
    value: float,
    *,
    name: str,
) -> float:
    """Validate a probability between zero and one."""

    if isinstance(value, bool) or not isinstance(
        value,
        (int, float, np.integer, np.floating),
    ):
        raise TypeError(
            f"{name} must be numeric. "
            "Use a decimal such as 0.10 for 10%."
        )

    value = float(value)

    if not 0 < value < 1:
        raise ValueError(
            f"{name} must be between 0 and 1. "
            f"You entered {value}. "
            "Use a decimal such as 0.10 for 10%."
        )

    return value


# Backward-compatible aliases.
findn_hyp = calculate_hypergeometric_sample_size
smallsameval = evaluate_hypergeometric_plan