"""Data models returned by the lotsampling library."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray


@dataclass(frozen=True)
class SamplingPlanResult:
    """Results from evaluating a zero-acceptance sampling plan.

    Attributes
    ----------
    nonconformance_rates:
        Proportions of nonconforming units evaluated by the model.

    acceptance_probabilities:
        Probability of accepting the lot at each nonconformance rate.

    average_fraction_inspected:
        Expected proportion of the lot that will be inspected.

    average_outgoing_quality:
        Expected outgoing nonconformance rate after rectifying inspection.

    aoql:
        Average Outgoing Quality Limit.

    equal_risk_point:
        Nonconformance rate where the acceptance probability is about 50%.

    lot_tolerance:
        Nonconformance rate where the acceptance probability is about 10%.

    rejectable_quality_level:
        Nonconformance rate where the acceptance probability is about 5%.
    """

    nonconformance_rates: NDArray[np.float64]
    acceptance_probabilities: NDArray[np.float64]
    average_fraction_inspected: NDArray[np.float64]
    average_outgoing_quality: NDArray[np.float64]
    aoql: float
    equal_risk_point: float
    lot_tolerance: float
    rejectable_quality_level: float

    def summary(self) -> dict[str, float]:
        """Return the primary plan metrics as a dictionary."""

        return {
            "AOQL": self.aoql,
            "Equal Risk Point": self.equal_risk_point,
            "Lot Tolerance": self.lot_tolerance,
            "Rejectable Quality Level": self.rejectable_quality_level,
        }