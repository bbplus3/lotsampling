"""Streamlit interface for the lotsampling Python library."""

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from lotsampling import (
    calculate_binomial_sample_size,
    calculate_hypergeometric_sample_size,
    evaluate_binomial_plan,
    evaluate_hypergeometric_plan,
    plot_operating_characteristic,
    plot_sampling_summary,
)


# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Lot Sampling Calculator",
    page_icon="📦",
    layout="wide",
)


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def format_percentage(value: float) -> str:
    """Format a decimal value as a percentage."""

    return f"{value:.2%}"


def display_plan_metrics(result) -> None:
    """Display the primary sampling-plan metrics."""

    st.subheader("Sampling Plan Results")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="AOQL",
            value=format_percentage(result.aoql),
            help=(
                "Average Outgoing Quality Limit. This is the maximum "
                "expected outgoing nonconformance rate under rectifying "
                "inspection."
            ),
        )

    with col2:
        st.metric(
            label="Equal Risk Point",
            value=format_percentage(result.equal_risk_point),
            help=(
                "The nonconformance rate where the probability of accepting "
                "the lot is approximately 50%."
            ),
        )

    with col3:
        st.metric(
            label="Lot Tolerance",
            value=format_percentage(result.lot_tolerance),
            help=(
                "The nonconformance rate where the probability of accepting "
                "the lot is approximately 10%."
            ),
        )

    with col4:
        st.metric(
            label="Rejectable Quality Level",
            value=format_percentage(
                result.rejectable_quality_level
            ),
            help=(
                "The nonconformance rate where the probability of accepting "
                "the lot is approximately 5%."
            ),
        )


def display_plan_plots(result) -> None:
    """Create and display sampling-plan plots."""

    st.subheader("Sampling Plan Visualizations")

    summary_figure = plot_sampling_summary(result)
    st.pyplot(summary_figure, use_container_width=True)
    plt.close(summary_figure)

    oc_figure = plot_operating_characteristic(result)
    st.pyplot(oc_figure, use_container_width=True)
    plt.close(oc_figure)


def display_plan_data(result) -> None:
    """Display the calculated curve values in a table."""

    results_table = pd.DataFrame(
        {
            "Nonconformance Rate": result.nonconformance_rates,
            "Probability of Acceptance": (
                result.acceptance_probabilities
            ),
            "Average Outgoing Quality": (
                result.average_outgoing_quality
            ),
            "Average Fraction Inspected": (
                result.average_fraction_inspected
            ),
        }
    )

    with st.expander("View calculated data"):
        st.dataframe(
            results_table,
            use_container_width=True,
            hide_index=True,
        )

        csv_data = results_table.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="Download results as CSV",
            data=csv_data,
            file_name="sampling_plan_results.csv",
            mime="text/csv",
        )


def display_plan_results(result) -> None:
    """Display metrics, plots, and calculated data."""

    display_plan_metrics(result)
    display_plan_plots(result)
    display_plan_data(result)


# ---------------------------------------------------------------------------
# Main application heading
# ---------------------------------------------------------------------------

st.title("📦 Lot Sampling Calculator")

st.markdown(
    """
    Create and evaluate **zero-acceptance sampling plans** for quality
    control.

    Use a **binomial plan** for continuous production or large lots.
    Use a **hypergeometric plan** for finite, isolated lots where sampling
    occurs without replacement.
    """
)

st.info(
    "Enter percentages as decimals. For example, enter 0.05 for 5% "
    "and 0.20 for 20%."
)


# ---------------------------------------------------------------------------
# Sidebar controls
# ---------------------------------------------------------------------------

st.sidebar.header("Sampling Plan Setup")

distribution = st.sidebar.radio(
    "Select a sampling model",
    options=[
        "Binomial",
        "Hypergeometric",
    ],
    help=(
        "Choose Binomial for continuous or large-lot sampling. "
        "Choose Hypergeometric for finite isolated lots."
    ),
)

operation = st.sidebar.radio(
    "Select an operation",
    options=[
        "Calculate Sample Size",
        "Evaluate Sampling Plan",
    ],
    help=(
        "Calculate Sample Size determines the minimum required sample. "
        "Evaluate Sampling Plan analyzes a sample size you already have."
    ),
)


# ---------------------------------------------------------------------------
# Binomial sampling
# ---------------------------------------------------------------------------

if distribution == "Binomial":

    st.header("Binomial Sampling Plan")

    st.write(
        "Use this model when the lot is large, production is continuous, "
        "or the binomial distribution is an appropriate approximation."
    )

    if operation == "Calculate Sample Size":

        st.subheader("Calculate a Required Sample Size")

        max_nonconformance = st.number_input(
            "Maximum nonconformance rate",
            min_value=0.001,
            max_value=0.999,
            value=0.20,
            step=0.01,
            format="%.3f",
            help=(
                "Enter the nonconformance rate the plan should protect "
                "against. For example, enter 0.20 for 20%."
            ),
        )

        consumer_risk = st.number_input(
            "Consumer risk",
            min_value=0.001,
            max_value=0.999,
            value=0.05,
            step=0.01,
            format="%.3f",
            help=(
                "Enter the maximum probability of accepting a lot at the "
                "specified nonconformance rate. Enter 0.05 for 5%."
            ),
        )

        st.caption(
            "This calculation assumes a zero-acceptance plan. The lot is "
            "accepted only when no nonconforming units are found."
        )

        if st.button(
            "Calculate Binomial Sample Size",
            type="primary",
        ):
            try:
                required_sample_size = (
                    calculate_binomial_sample_size(
                        max_nonconformance=max_nonconformance,
                        consumer_risk=consumer_risk,
                    )
                )

                st.success(
                    "The required sample size is "
                    f"{required_sample_size} units."
                )

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Required Sample Size",
                        required_sample_size,
                    )

                with col2:
                    st.metric(
                        "Nonconformance Rate",
                        format_percentage(max_nonconformance),
                    )

                with col3:
                    st.metric(
                        "Consumer Risk",
                        format_percentage(consumer_risk),
                    )

            except (TypeError, ValueError) as error:
                st.error(str(error))

    else:

        st.subheader("Evaluate an Existing Binomial Plan")

        col1, col2 = st.columns(2)

        with col1:
            lot_size = int(
                st.number_input(
                    "Lot size",
                    min_value=1,
                    value=500,
                    step=1,
                    help=(
                        "Enter the total number of units in the lot. "
                        "The sample size cannot exceed this value."
                    ),
                )
            )

        with col2:
            sample_size = int(
                st.number_input(
                    "Sample size",
                    min_value=1,
                    value=30,
                    step=1,
                    help=(
                        "Enter the number of units inspected from each lot."
                    ),
                )
            )

        max_nonconformance = st.number_input(
            "Maximum nonconformance rate shown on the curves",
            min_value=0.001,
            max_value=1.0,
            value=0.20,
            step=0.01,
            format="%.3f",
            help=(
                "This controls the upper limit of the chart's horizontal "
                "axis. Enter 0.20 to evaluate rates from 0% through 20%."
            ),
        )

        curve_points = int(
            st.number_input(
                "Number of curve points",
                min_value=2,
                max_value=5001,
                value=201,
                step=1,
                help=(
                    "A larger value produces a smoother curve but requires "
                    "slightly more computation."
                ),
            )
        )

        if sample_size > lot_size:
            st.warning(
                "The sample size is currently greater than the lot size. "
                "Reduce the sample size or increase the lot size."
            )

        if st.button(
            "Evaluate Binomial Plan",
            type="primary",
        ):
            try:
                result = evaluate_binomial_plan(
                    sample_size=sample_size,
                    lot_size=lot_size,
                    max_nonconformance=max_nonconformance,
                    points=curve_points,
                )

                st.success(
                    "The binomial sampling plan was evaluated successfully."
                )

                display_plan_results(result)

            except (TypeError, ValueError) as error:
                st.error(str(error))


# ---------------------------------------------------------------------------
# Hypergeometric sampling
# ---------------------------------------------------------------------------

else:

    st.header("Hypergeometric Sampling Plan")

    st.write(
        "Use this model for finite, isolated lots where units are sampled "
        "without replacement."
    )

    if operation == "Calculate Sample Size":

        st.subheader("Calculate a Required Sample Size")

        col1, col2 = st.columns(2)

        with col1:
            lot_size = int(
                st.number_input(
                    "Lot size",
                    min_value=1,
                    value=50,
                    step=1,
                    help=(
                        "Enter the total number of units in the isolated lot."
                    ),
                )
            )

        with col2:
            defect_count = int(
                st.number_input(
                    "Nonconforming units in the protected condition",
                    min_value=1,
                    value=5,
                    step=1,
                    help=(
                        "Enter the number of nonconforming units representing "
                        "the condition the plan should detect. For example, "
                        "5 units in a lot of 50 represents 10%."
                    ),
                )
            )

        consumer_risk = st.number_input(
            "Consumer risk",
            min_value=0.001,
            max_value=0.999,
            value=0.10,
            step=0.01,
            format="%.3f",
            help=(
                "Enter the maximum probability of accepting the lot when it "
                "contains the specified number of nonconforming units."
            ),
        )

        if lot_size > 0:
            protected_rate = defect_count / lot_size

            st.caption(
                "The protected condition represents approximately "
                f"{protected_rate:.2%} nonconforming units."
            )

        if defect_count > lot_size:
            st.warning(
                "The number of nonconforming units cannot exceed the "
                "lot size."
            )

        if st.button(
            "Calculate Hypergeometric Sample Size",
            type="primary",
        ):
            try:
                required_sample_size = (
                    calculate_hypergeometric_sample_size(
                        lot_size=lot_size,
                        defect_count=defect_count,
                        consumer_risk=consumer_risk,
                    )
                )

                st.success(
                    "The required sample size is "
                    f"{required_sample_size} units."
                )

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric(
                        "Required Sample Size",
                        required_sample_size,
                    )

                with col2:
                    st.metric(
                        "Lot Size",
                        lot_size,
                    )

                with col3:
                    st.metric(
                        "Protected Rate",
                        format_percentage(
                            defect_count / lot_size
                        ),
                    )

                with col4:
                    st.metric(
                        "Consumer Risk",
                        format_percentage(consumer_risk),
                    )

            except (TypeError, ValueError) as error:
                st.error(str(error))

    else:

        st.subheader("Evaluate an Existing Hypergeometric Plan")

        col1, col2 = st.columns(2)

        with col1:
            lot_size = int(
                st.number_input(
                    "Lot size",
                    min_value=1,
                    value=50,
                    step=1,
                    help=(
                        "Enter the total number of units in the isolated lot."
                    ),
                )
            )

        with col2:
            sample_size = int(
                st.number_input(
                    "Sample size",
                    min_value=1,
                    value=10,
                    step=1,
                    help=(
                        "Enter the number of units sampled without "
                        "replacement."
                    ),
                )
            )

        if sample_size > lot_size:
            st.warning(
                "The sample size is currently greater than the lot size. "
                "Reduce the sample size or increase the lot size."
            )

        if st.button(
            "Evaluate Hypergeometric Plan",
            type="primary",
        ):
            try:
                result = evaluate_hypergeometric_plan(
                    sample_size=sample_size,
                    lot_size=lot_size,
                )

                st.success(
                    "The hypergeometric sampling plan was evaluated "
                    "successfully."
                )

                display_plan_results(result)

            except (TypeError, ValueError) as error:
                st.error(str(error))


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

st.divider()

st.caption(
    "This calculator evaluates zero-acceptance sampling plans. "
    "Results should be reviewed alongside applicable quality standards, "
    "customer requirements, and engineering judgment."
)