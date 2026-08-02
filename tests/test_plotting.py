import matplotlib.pyplot as plt
import pytest
from matplotlib.figure import Figure

from lotsampling import (
    evaluate_binomial_plan,
    evaluate_hypergeometric_plan,
    plot_operating_characteristic,
    plot_sampling_summary,
)


def test_plot_sampling_summary_returns_figure_for_binomial_plan():
    result = evaluate_binomial_plan(
        sample_size=30,
        lot_size=500,
    )

    figure = plot_sampling_summary(result)

    assert isinstance(figure, Figure)
    assert len(figure.axes) == 3

    plt.close(figure)


def test_plot_operating_characteristic_returns_figure_for_binomial_plan():
    result = evaluate_binomial_plan(
        sample_size=30,
        lot_size=500,
    )

    figure = plot_operating_characteristic(result)

    assert isinstance(figure, Figure)
    assert len(figure.axes) == 1

    plt.close(figure)


def test_plot_sampling_summary_returns_figure_for_hypergeometric_plan():
    result = evaluate_hypergeometric_plan(
        sample_size=10,
        lot_size=50,
    )

    figure = plot_sampling_summary(result)

    assert isinstance(figure, Figure)
    assert len(figure.axes) == 3

    plt.close(figure)


def test_plot_operating_characteristic_returns_figure_for_hypergeometric_plan():
    result = evaluate_hypergeometric_plan(
        sample_size=10,
        lot_size=50,
    )

    figure = plot_operating_characteristic(result)

    assert isinstance(figure, Figure)
    assert len(figure.axes) == 1

    plt.close(figure)


@pytest.mark.parametrize(
    "plot_function",
    [
        plot_sampling_summary,
        plot_operating_characteristic,
    ],
)
def test_plot_functions_reject_invalid_result(plot_function):
    with pytest.raises(
        TypeError,
        match="result must be a SamplingPlanResult",
    ):
        plot_function("not a sampling result")