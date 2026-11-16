# lotsampling

A Python library for creating, evaluating, and visualizing zero-acceptance acceptance sampling plans.

## Features

- Binomial sampling plans
- Hypergeometric sampling plans
- AOQL calculations
- Operating Characteristic (OC) curves
- Streamlit demo application

## Installation

```bash
pip install lotsampling
```

## Example

```python
from lotsampling import evaluate_binomial_plan

result = evaluate_binomial_plan(
    sample_size=30,
    lot_size=500,
)

print(result.aoql)
```

## License

MIT
