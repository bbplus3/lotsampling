import numpy as np
import pytest
from scipy.stats import hypergeom

from lotsampling import (
    calculate_hypergeometric_sample_size,
    evaluate_hypergeometric_plan,
)


def test_calculate_hypergeometric_sample_size():
    sample_size = calculate_hypergeometric_sample_size(
        lot_size=50,
        defect_count=5,
        consumer_risk=0.10,
    )

    assert sample_size == 18


def test_calculated_sample_size_meets_consumer_risk():
    lot_size = 50
    defect_count = 5
    consumer_risk = 0.10

    sample_size = calculate_hypergeometric_sample_size(
        lot_size=lot_size,
        defect_count=defect_count,
        consumer_risk=consumer_risk,
    )

    acceptance_probability = hypergeom.cdf(
        0,
        lot_size,
        defect_count,
        sample_size,
    )

    assert acceptance_probability <= consumer_risk


def test_evaluate_hypergeometric_plan_returns_expected_values():
    result = evaluate_hypergeometric_plan(
        sample_size=10,
        lot_size=50,
    )

    assert isinstance(result.nonconformance_rates, np.ndarray)
    assert isinstance(result.acceptance_probabilities, np.ndarray)
    assert isinstance(result.average_fraction_inspected, np.ndarray)
    assert isinstance(result.average_outgoing_quality, np.ndarray)

    assert len(result.nonconformance_rates) == 51
    assert len(result.acceptance_probabilities) == 51
    assert len(result.average_fraction_inspected) == 51
    assert len(result.average_outgoing_quality) == 51

    assert result.aoql == pytest.approx(
        0.025397134172818064
    )


def test_acceptance_probability_starts_at_one():
    result = evaluate_hypergeometric_plan(
        sample_size=10,
        lot_size=50,
    )

    assert result.acceptance_probabilities[0] == pytest.approx(1.0)


def test_acceptance_probability_decreases():
    result = evaluate_hypergeometric_plan(
        sample_size=10,
        lot_size=50,
    )

    differences = np.diff(result.acceptance_probabilities)

    assert np.all(differences <= 0)


def test_sample_size_cannot_exceed_lot_size():
    with pytest.raises(
        ValueError,
        match="sample_size cannot be greater than lot_size",
    ):
        evaluate_hypergeometric_plan(
            sample_size=51,
            lot_size=50,
        )


def test_defect_count_cannot_exceed_lot_size():
    with pytest.raises(
        ValueError,
        match="defect_count cannot be greater than lot_size",
    ):
        calculate_hypergeometric_sample_size(
            lot_size=50,
            defect_count=51,
            consumer_risk=0.10,
        )


@pytest.mark.parametrize(
    "consumer_risk",
    [
        0.0,
        1.0,
        -0.10,
        5.0,
    ],
)
def test_invalid_consumer_risk(consumer_risk):
    with pytest.raises(ValueError):
        calculate_hypergeometric_sample_size(
            lot_size=50,
            defect_count=5,
            consumer_risk=consumer_risk,
        )