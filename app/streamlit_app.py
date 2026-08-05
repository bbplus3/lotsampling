"""Streamlit interface for the lotsampling Python library."""

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from lotsampling import (
    calculate_binomial_sample_size,
    calculate_hypergeometric_sample_size,
    evaluate_binomial_plan,
    evaluate_hypergeometric_plan,
    plot_continuous_sampling_chain,
    plot_escape_histogram,
    plot_operating_characteristic,
    plot_sampling_summary,
    plot_state_allocation,
    simulate_continuous_sampling,
    simulate_sampling_escapes,
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
        "Continuous Sampling",
    ],
    help=(
        "Choose Binomial for large-lot acceptance sampling, "
        "Hypergeometric for finite isolated lots, or Continuous "
        "Sampling to simulate inspection states and escaped defects."
    ),
)

operation = None

if distribution in {"Binomial", "Hypergeometric"}:
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

elif distribution == "Hypergeometric":
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
# Continuous sampling simulation
# ---------------------------------------------------------------------------

else:
    st.header("Continuous Sampling Simulation")

    st.markdown(
        """
        Simulate a continuous inspection process using a Markov chain.

        With the default six-state design:

        - States 1–5 represent progress toward reduced sampling.
        - A successful inspection advances the process one state.
        - A failure returns the process to State 1.
        - State 6 represents reduced sampling.
        - Defects not selected for inspection in State 6 are escapes.
        """
    )

    simulation_type = st.radio(
        "Select a simulation",
        options=[
            "Markov Chain",
            "Escaped Defects",
        ],
        horizontal=True,
    )

    probability_col1, probability_col2 = st.columns(2)

    with probability_col1:
        selection_probability = st.number_input(
            "Selection probability",
            min_value=0.0,
            max_value=1.0,
            value=1 / 3,
            step=0.01,
            format="%.3f",
            help=(
                "Probability that a unit is selected for inspection while "
                "the process is in the reduced-sampling state. Enter 0.333 "
                "to inspect approximately one-third of units."
            ),
        )

    with probability_col2:
        failure_probability = st.number_input(
            "Failure probability",
            min_value=0.0,
            max_value=1.0,
            value=0.05,
            step=0.01,
            format="%.3f",
            help=(
                "Probability that a unit is defective. Enter 0.05 for a "
                "5% failure probability."
            ),
        )

    settings_col1, settings_col2, settings_col3 = st.columns(3)

    with settings_col1:
        runs = int(
            st.number_input(
                "Simulation runs",
                min_value=1,
                value=1000,
                step=100,
                help=(
                    "Number of Markov-chain transitions or production "
                    "batches to simulate."
                ),
            )
        )

    with settings_col2:
        states = int(
            st.number_input(
                "Number of states",
                min_value=2,
                value=6,
                step=1,
                help=(
                    "The default represents five inspection-progress "
                    "states followed by one reduced-sampling state."
                ),
            )
        )

    with settings_col3:
        random_state = int(
            st.number_input(
                "Random seed",
                min_value=0,
                value=0,
                step=1,
                help=(
                    "Using the same seed reproduces the same simulation."
                ),
            )
        )

    if simulation_type == "Markov Chain":
        st.subheader("Markov-Chain Simulation")

        if st.button(
            "Run Markov-Chain Simulation",
            type="primary",
        ):
            try:
                result = simulate_continuous_sampling(
                    selection_probability=selection_probability,
                    failure_probability=failure_probability,
                    runs=runs,
                    states=states,
                    random_state=random_state,
                )

                st.success("The Markov-chain simulation completed.")

                metric_col1, metric_col2, metric_col3 = st.columns(3)

                with metric_col1:
                    st.metric("Simulation Runs", runs)

                with metric_col2:
                    st.metric(
                        "Time in Sampling State",
                        f"{result.state_proportions[-1]:.2%}",
                        help=(
                            "Proportion of the simulation spent in the "
                            "final reduced-sampling state."
                        ),
                    )

                with metric_col3:
                    st.metric(
                        "Final State",
                        int(result.chain[-1]),
                    )

                state_figure = plot_state_allocation(result)
                st.pyplot(
                    state_figure,
                    use_container_width=True,
                )
                plt.close(state_figure)

                transition_figure = plot_continuous_sampling_chain(
                    selection_probability=selection_probability,
                    failure_probability=failure_probability,
                    states=states,
                )
                st.pyplot(
                    transition_figure,
                    use_container_width=True,
                )
                plt.close(transition_figure)

                state_table = pd.DataFrame(
                    {
                        "State": range(1, states + 1),
                        "Proportion of Time": result.state_proportions,
                        "Percentage of Time": (
                            result.state_proportions * 100
                        ),
                    }
                )

                with st.expander("View state allocation"):
                    st.dataframe(
                        state_table,
                        use_container_width=True,
                        hide_index=True,
                    )

                transition_table = pd.DataFrame(
                    result.transition_matrix,
                    index=[
                        f"From State {state}"
                        for state in range(1, states + 1)
                    ],
                    columns=[
                        f"To State {state}"
                        for state in range(1, states + 1)
                    ],
                )

                with st.expander("View transition matrix"):
                    st.dataframe(
                        transition_table,
                        use_container_width=True,
                    )

                chain_table = pd.DataFrame(
                    {
                        "Step": range(len(result.chain)),
                        "State": result.chain,
                    }
                )

                with st.expander("View simulated state sequence"):
                    st.dataframe(
                        chain_table,
                        use_container_width=True,
                        hide_index=True,
                    )

                    st.download_button(
                        label="Download state sequence as CSV",
                        data=chain_table.to_csv(
                            index=False
                        ).encode("utf-8"),
                        file_name="continuous_sampling_chain.csv",
                        mime="text/csv",
                    )

            except (TypeError, ValueError) as error:
                st.error(str(error))

    else:
        st.subheader("Escaped-Defect Simulation")

        batch_size = int(
            st.number_input(
                "Batch size",
                min_value=1,
                value=100,
                step=10,
                help=(
                    "Number of production units generated during each "
                    "simulation run."
                ),
            )
        )

        st.caption(
            "Full-inspection states catch every simulated defect. In the "
            "final sampling state, defective units that are not selected "
            "for inspection are counted as escapes."
        )

        if st.button(
            "Run Escape Simulation",
            type="primary",
        ):
            try:
                result = simulate_sampling_escapes(
                    selection_probability=selection_probability,
                    failure_probability=failure_probability,
                    runs=runs,
                    batch_size=batch_size,
                    states=states,
                    random_state=random_state,
                )

                st.success("The escape simulation completed.")

                metric_col1, metric_col2, metric_col3, metric_col4 = (
                    st.columns(4)
                )

                with metric_col1:
                    st.metric(
                        "Mean Escapes per Batch",
                        f"{result.mean_escapes:.3f}",
                    )

                with metric_col2:
                    st.metric(
                        "Total Escapes",
                        result.total_escapes,
                    )

                with metric_col3:
                    st.metric(
                        "Escape Rate",
                        f"{result.escape_rate:.2%}",
                        help=(
                            "Escaped defects divided by all generated "
                            "defects."
                        ),
                    )

                with metric_col4:
                    st.metric(
                        "Sampling-State Runs",
                        result.sampling_runs,
                    )

                histogram = plot_escape_histogram(result)
                st.pyplot(
                    histogram,
                    use_container_width=True,
                )
                plt.close(histogram)

                escape_table = pd.DataFrame(
                    {
                        "Run": range(1, runs + 1),
                        "Process State": result.process_states,
                        "Generated Defects": result.defects,
                        "Caught Defects": result.catches,
                        "Escaped Defects": result.escapes,
                    }
                )

                with st.expander("View escape simulation data"):
                    st.dataframe(
                        escape_table,
                        use_container_width=True,
                        hide_index=True,
                    )

                    st.download_button(
                        label="Download escape results as CSV",
                        data=escape_table.to_csv(
                            index=False
                        ).encode("utf-8"),
                        file_name="escaped_defect_simulation.csv",
                        mime="text/csv",
                    )

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
