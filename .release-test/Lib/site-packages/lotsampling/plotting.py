import matplotlib

# Use a non-GUI backend so plotting works during testing
matplotlib.use("Agg")

"""Visualization functions for sampling-plan results."""

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from .models import SamplingPlanResult


def plot_sampling_summary(
    result: SamplingPlanResult,
) -> Figure:
    """Plot the three primary sampling-plan curves.

    Parameters
    ----------
    result:
        Result returned by ``evaluate_binomial_plan`` or
        ``evaluate_hypergeometric_plan``.

    Returns
    -------
    matplotlib.figure.Figure
        A Matplotlib figure containing acceptance probability,
        average outgoing quality, and average fraction inspected.
    """

    _validate_result(result)

    figure, axes = plt.subplots(
        3,
        1,
        figsize=(10, 11),
        constrained_layout=True,
    )

    axes[0].plot(
        result.nonconformance_rates,
        result.acceptance_probabilities,
    )
    axes[0].set_title("Probability of Acceptance")
    axes[0].set_ylabel("Probability")

    axes[1].plot(
        result.nonconformance_rates,
        result.average_outgoing_quality,
    )
    axes[1].axhline(
        result.aoql,
        linestyle="--",
        label=f"AOQL: {result.aoql:.4f}",
    )
    axes[1].set_title("Average Outgoing Quality")
    axes[1].set_ylabel("Outgoing quality")
    axes[1].legend()

    axes[2].plot(
        result.nonconformance_rates,
        result.average_fraction_inspected,
    )
    axes[2].set_title("Average Fraction Inspected")
    axes[2].set_ylabel("Fraction inspected")

    for axis in axes:
        axis.set_xlabel("Proportion nonconforming")
        axis.grid(True)

    return figure


def plot_operating_characteristic(
    result: SamplingPlanResult,
) -> Figure:
    """Plot the operating-characteristic curve for a sampling plan."""

    _validate_result(result)

    figure, axis = plt.subplots(
        figsize=(9, 5),
        constrained_layout=True,
    )

    axis.plot(
        result.nonconformance_rates,
        result.acceptance_probabilities,
        label="Probability of acceptance",
    )

    axis.axvline(
        result.equal_risk_point,
        linestyle="--",
        label=(
            "Equal risk point: "
            f"{result.equal_risk_point:.4f}"
        ),
    )

    axis.set_title("Operating-Characteristic Curve")
    axis.set_xlabel("Proportion nonconforming")
    axis.set_ylabel("Probability of acceptance")
    axis.set_ylim(0, 1.05)
    axis.grid(True)
    axis.legend()

    return figure


def _validate_result(result: SamplingPlanResult) -> None:
    """Provide a friendly message when the wrong input is supplied."""

    if not isinstance(result, SamplingPlanResult):
        raise TypeError(
            "result must be a SamplingPlanResult returned by "
            "evaluate_binomial_plan() or "
            "evaluate_hypergeometric_plan()."
        )


# Backward-compatible aliases.
plot_all3 = plot_sampling_summary
plot_oc_curve = plot_operating_characteristic