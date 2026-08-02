\# lotsampling



A Python library for creating, evaluating, and visualizing zero-acceptance acceptance sampling plans.



\## Features



\- Binomial sampling plans

\- Hypergeometric sampling plans

\- AOQL calculations

\- Operating Characteristic (OC) curves

\- Streamlit demo application



\## Installation



```bash

pip install lotsampling

```



\## Example



```python

from lotsampling import evaluate\_binomial\_plan



result = evaluate\_binomial\_plan(

&#x20;   sample\_size=30,

&#x20;   lot\_size=500,

)



print(result.aoql)

```



\## License



MIT

