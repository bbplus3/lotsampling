"""Create, evaluate, and visualize acceptance sampling plans."""

from .binomial import (
    calculate_binomial_sample_size,
    evaluate_binomial_plan,
    findn,
    lotsameval,
)
from .hypergeometric import (
    calculate_hypergeometric_sample_size,
    evaluate_hypergeometric_plan,
    findn_hyp,
    smallsameval,
)
from .models import SamplingPlanResult
from .plotting import (
    plot_all3,
    plot_oc_curve,
    plot_operating_characteristic,
    plot_sampling_summary,
)

__all__ = [
    "SamplingPlanResult",
    "calculate_binomial_sample_size",
    "calculate_hypergeometric_sample_size",
    "evaluate_binomial_plan",
    "evaluate_hypergeometric_plan",
    "plot_sampling_summary",
    "plot_operating_characteristic",
    # Legacy aliases
    "findn",
    "findn_hyp",
    "lotsameval",
    "smallsameval",
    "plot_all3",
    "plot_oc_curve",
]

__version__ = "0.2.0"