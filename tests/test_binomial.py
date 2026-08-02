import numpy as np
import pytest

from lotsampling import (
    calculate_binomial_sample_size,
    evaluate_binomial_plan,
)


def test_calculate_binomial_sample_size():
    sample_size = calculate_binomial_sample_size(
        max_nonconformance=0.20,
        consumer_risk=0.05,
    )

    assert sample_size == 14


def test_evaluate_binomial_plan_returns_expected_values():
    result = evaluate_binomial_plan(
        sample_size=30,
        lot_size=500,
    )

    assert isinstance(result.nonconformance_rates, np.ndarray)
    assert isinstance(result.acceptance_probabilities, np.ndarray)
    assert isinstance(result.average_fraction_inspected, np.ndarray)
    assert isinstance(result.average_outgoing_quality, np.ndarray)

    assert len(result.nonconformance_rates) == 201
    assert len(result.acceptance_probabilities) == 201
    assert len(result.average_fraction_inspected) == 201
    assert len(result.average_outgoing_quality) == 201

    assert result.aoql == pytest.approx(
        0.011338431647997364
    )

    assert 0 <= result.equal_risk_point <= 1
    assert 0 <= result.lot_tolerance <= 1
    assert 0 <= result.rejectable_quality_level <= 1


def test_acceptance_probability_starts_at_one():
    result = evaluate_binomial_plan(
        sample_size=30,
        lot_size=500,
    )

    assert result.acceptance_probabilities[0] == pytest.approx(1.0)


def test_acceptance_probability_decreases():
    result = evaluate_binomial_plan(
        sample_size=30,
        lot_size=500,
    )

    differences = np.diff(result.acceptance_probabilities)

    assert np.all(differences <= 0)


def test_sample_size_cannot_exceed_lot_size():
    with pytest.raises(
        ValueError,
        match="sample_size cannot be greater than lot_size",
    ):
        evaluate_binomial_plan(
            sample_size=501,
            lot_size=500,
        )


@pytest.mark.parametrize(
    "max_nonconformance, consumer_risk",
    [
        (0.0, 0.05),
        (1.0, 0.05),
        (0.20, 0.0),
        (0.20, 1.0),
        (5.0, 0.05),
        (0.20, 5.0),
    ],
)
def test_invalid_probabilities(
    max_nonconformance,
    consumer_risk,
):
    with pytest.raises(ValueError):
        calculate_binomial_sample_size(
            max_nonconformance=max_nonconformance,
            consumer_risk=consumer_risk,
        )

def test_result_summary_returns_expected_metrics():
    result = evaluate_binomial_plan(
        sample_size=30,
        lot_size=500,
    )

    summary = result.summary()

    assert summary["AOQL"] == result.aoql
    assert summary["Equal Risk Point"] == result.equal_risk_point
    assert summary["Lot Tolerance"] == result.lot_tolerance
    assert (
        summary["Rejectable Quality Level"]
        == result.rejectable_quality_level
    )