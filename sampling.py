import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import hypergeom

# --- Functions ---
def lotsameval(n, N, maxp=0.2):
    Probs = (maxp / 200) * np.arange(201)
    PA = np.array([np.sum([np.math.comb(n, x) * (p**x) * ((1-p)**(n-x)) for x in range(1)]) for p in Probs])
    AFI = 1 - (1 - n/N) * PA
    AOQ = Probs * (1 - AFI)
    AOQL = ((1 - n/N)/(1 + n))*(n/(n + 1))**n
    ERP = 1 - (0.5)**(1/n)
    LTol = 1 - (0.1)**(1/n)
    RQL = 1 - (0.05)**(1/n)
    return Probs, PA, AFI, AOQ, AOQL, ERP, LTol, RQL

def smallsameval(n, N):
    D = np.arange(0, N+1)
    PA = hypergeom.cdf(0, N, D, n)
    AFI = 1 - (1 - n/N) * PA
    AOQ = D * (1 - AFI) / N
    AOQL = np.max(AOQ)
    ERP = D[PA <= 0.5][0] / N if np.any(PA <= 0.5) else np.nan
    LTol = D[PA <= 0.1][0] / N if np.any(PA <= 0.1) else np.nan
    RQL = D[PA <= 0.05][0] / N if np.any(PA <= 0.05) else np.nan
    return D / N, PA, AFI, AOQ, AOQL, ERP, LTol, RQL

def plot_all3(Probs, PA, AFI, AOQ):
    fig, axs = plt.subplots(3, 1, figsize=(10, 10))
    axs[0].plot(Probs, PA, label="PA")
    axs[0].set_title("Probability of Acceptance")
    axs[1].plot(Probs, AOQ, label="AOQ")
    axs[1].set_title("Average Outgoing Quality")
    axs[2].plot(Probs, AFI, label="AFI")
    axs[2].set_title("Average Fraction Inspected")
    for ax in axs:
        ax.legend()
        ax.grid(True)
    st.pyplot(fig)

def plot_OC_curve(Probs, PA, ERP):
    fig, ax = plt.subplots()
    ax.plot(Probs, PA, 'b-', label="PA")
    ax.axvline(x=ERP, color='red', linestyle='--', label=f"ERP = {ERP:.4f}")
    ax.set_title("OC Curve with Equal Risk Point")
    ax.set_xlabel("Probability of nonConformance")
    ax.set_ylabel("Probability of Acceptance")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

def findn(maxp, alp):
    return int(np.ceil(np.log(alp) / np.log(1 - maxp)))

def findn_hyp(N, D, alp):
    maxp = D / N
    n = int(np.ceil(np.log(alp) / np.log(1 - maxp)))
    PA = hypergeom.cdf(0, N, D, n)
    while PA <= alp:
        n -= 1
        PA = hypergeom.cdf(0, N, D, n)
    return n + 1

# --- Streamlit UI ---
st.set_page_config(page_title="Sampling Plan Calculator", layout="wide")
st.title("📦 Creating and Evaluating Sampling Plans")
st.sidebar.header("🔬 Sampling Plan Options")

st.markdown("""
### 🧪 Quality Control Dashboard
Use this tool to inspect and evaluate lot-based sampling plans. Choose between Binomial or Hypergeometric models, and either calculate required sample sizes or assess plan parameters like AOQL, ERP, and more.
""")

eord = st.sidebar.radio("Distribution Type", ["binom", "hyp"], format_func=lambda x: {
    "binom": "Binomial / Continuous Lot",
    "hyp": "Hypergeometric / Isolated Lot"
}[x])

aord = st.sidebar.radio("Create or Evaluate", ["create", "eval"], format_func=lambda x: {
    "create": "Calculate Sample Size",
    "eval": "Evaluate Sampling Plan"
}[x])

if eord == "binom":
    if aord == "create":
        maxp = st.sidebar.number_input("Probability of nonConformance", value=0.2, min_value=0.0, max_value=1.0, step=0.01)
        alp = st.sidebar.number_input("Consumer Risk (alpha)", value=0.05, min_value=0.0, max_value=1.0, step=0.01)
        if st.sidebar.button("Calculate Sample Size"):
            n = findn(maxp, alp)
            st.subheader("Sample Size Required")
            st.write(n)
    elif aord == "eval":
        maxp = st.sidebar.number_input("Probability of nonConformance", value=0.2, min_value=0.0, max_value=1.0, step=0.01)
        N = st.sidebar.number_input("Lot Size (N)", value=500)
        n = st.sidebar.number_input("Sample Size (n)", value=30)

        if st.sidebar.button("Evaluate Plan"):
            Probs, PA, AFI, AOQ, AOQL, ERP, LTol, RQL = lotsameval(n, N, maxp)
            st.subheader("Continuous Lots Parameters")
            st.write(f"**Average Outgoing Quality Limit (AOQL):** {AOQL:.4f}")
            st.write(f"**Equal Risk Point (ERP):** {ERP:.4f}")
            st.write(f"**Lot Tolerance (consumer risk = 0.1):** {LTol:.4f}")
            st.write(f"**Rejectable Quality Level (RQL = 0.05):** {RQL:.4f}")
            st.write(f"**Sample Size (n):** {n}")

            st.subheader("Continuous Lots Plots")
            plot_all3(Probs, PA, AFI, AOQ)
            plot_OC_curve(Probs, PA, ERP)

elif eord == "hyp":
    if aord == "create":
        N = st.sidebar.number_input("Lot Size (N)", value=50)
        D = st.sidebar.number_input("Defect Count (D)", value=5)
        alp = st.sidebar.number_input("Consumer Risk (alpha)", value=0.1, min_value=0.0, max_value=1.0, step=0.01)
        if st.sidebar.button("Calculate Sample Size"):
            n = findn_hyp(N, D, alp)
            st.subheader("Sample Size Required")
            st.write(n)
    elif aord == "eval":
        D = st.sidebar.number_input("Defect Count (D)", value=4)
        N = st.sidebar.number_input("Lot Size (N)", value=50)
        n = st.sidebar.number_input("Sample Size (n)", value=10)

        if st.sidebar.button("Evaluate Plan"):
            Probs, PA, AFI, AOQ, AOQL, ERP, LTol, RQL = smallsameval(n, N)
            st.subheader("Isolated Lot Parameters")
            st.write(f"**Average Outgoing Quality Limit (AOQL):** {AOQL:.4f}")
            st.write(f"**Equal Risk Point (ERP):** {ERP:.4f}")
            st.write(f"**Lot Tolerance (consumer risk = 0.1):** {LTol:.4f}")
            st.write(f"**Rejectable Quality Level (RQL = 0.05):** {RQL:.4f}")
            st.write(f"**Sample Size (n):** {n}")

            st.subheader("Isolated Lot Plots")
            plot_all3(Probs, PA, AFI, AOQ)

st.markdown("---")
st.subheader("Definitions")
st.markdown("""
- **Binomial/continuous lot**: Number of successes in repeated trials.
- **Hypergeometric/isolated lot**: Successes in draws without replacement.
- **Lot Size (N)**: Grouping of product, material, or service.
- **Sample Size (n)**: Number of units drawn from the lot.
- **Defect Count**: Expected number of defects per lot.
- **Probability of nonConformance**: Likelihood a unit is defective.
- **Consumer Risk (alpha)**: Chance of accepting a bad lot.
- **Producer Risk**: Chance of rejecting a good lot.
- **AOQL**: Max AOQ for a sampling plan.
- **ERP**: Quality level where consumer and producer risk are both 50%.
- **LTol / RQL**: Quality levels associated with specific rejection risks.
- **AOQ**: Average outgoing quality.
""")
