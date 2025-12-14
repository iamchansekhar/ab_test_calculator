import streamlit as st
import math
from scipy.stats import norm, beta

# -------------------------------------------------
# Page Configuration
# -------------------------------------------------
st.set_page_config(
    page_title="YourAnalyst • A/B Testing Toolkit",
    layout="centered"
)

# -------------------------------------------------
# Apple-style Minimal Theme
# -------------------------------------------------
st.markdown("""
<style>
:root {
    --primary: #ff5a36;
}
h1, h2, h3 {
    font-weight: 600;
}
button[kind="primary"] {
    background-color: var(--primary);
}
div[data-testid="metric-container"] {
    border-radius: 14px;
    padding: 14px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# Header
# -------------------------------------------------
st.title("YourAnalyst A/B Testing Toolkit")
st.caption("Clear experimentation insights for product teams")

st.divider()

# -------------------------------------------------
# Tabs
# -------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "Frequentist A/B Test",
    "Bayesian A/B Test",
    "Sample Size Calculator"
])

# =================================================
# TAB 1 — FREQUENTIST A/B TEST
# =================================================
with tab1:
    st.subheader("Frequentist A/B Test")

    st.write(
        "This test helps you determine whether the observed difference between "
        "two variants is **likely real or just random chance**."
    )

    test_type = st.radio(
        "Hypothesis type",
        ["Two-tailed", "One-tailed"],
        horizontal=True
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Variant A")
        visitors_a = st.number_input("Visitors", min_value=1, value=10000)
        conversions_a = st.number_input("Conversions", min_value=0, value=500)

    with col2:
        st.markdown("#### Variant B")
        visitors_b = st.number_input("Visitors ", min_value=1, value=9800)
        conversions_b = st.number_input("Conversions ", min_value=0, value=560)

    if st.button("Analyze Experiment", type="primary"):
        cr_a = conversions_a / visitors_a
        cr_b = conversions_b / visitors_b

        pooled = (conversions_a + conversions_b) / (visitors_a + visitors_b)
        se = math.sqrt(pooled * (1 - pooled) * (1/visitors_a + 1/visitors_b))

        z = (cr_b - cr_a) / se

        if test_type == "Two-tailed":
            p_value = 2 * (1 - norm.cdf(abs(z)))
        else:
            p_value = 1 - norm.cdf(z)

        lift = (cr_b - cr_a) / cr_a * 100

        ci_low = (cr_b - cr_a) - 1.96 * se
        ci_high = (cr_b - cr_a) + 1.96 * se

        st.divider()
        st.subheader("Results")

        m1, m2, m3 = st.columns(3)
        m1.metric("Conversion Rate A", f"{cr_a*100:.2f}%")
        m2.metric("Conversion Rate B", f"{cr_b*100:.2f}%")
        m3.metric("Lift", f"{lift:.2f}%")

        st.write(f"**P-value:** {p_value:.4f}")
        st.write(
            f"**95% Confidence Interval (B − A):** "
            f"[{ci_low*100:.2f}%, {ci_high*100:.2f}%]"
        )

        # -------------------------------
        # Plain English Explanation
        # -------------------------------
        with st.expander("What does this mean?"):
            if p_value < 0.05:
                st.write(
                    "The difference between Variant A and Variant B is unlikely "
                    "to be caused by random chance. This means Variant B is "
                    "very likely performing better than Variant A."
                )
            else:
                st.write(
                    "The observed difference could be due to randomness. "
                    "You do not yet have enough evidence to confidently say "
                    "that Variant B is better."
                )

        # -------------------------------
        # Mathematical Explanation
        # -------------------------------
        with st.expander("How is this calculated? (Math & Logic)"):
            st.markdown("""
**Step 1: Conversion Rates**

\\[
CR_A = \\frac{Conversions_A}{Visitors_A}
\\]

\\[
CR_B = \\frac{Conversions_B}{Visitors_B}
\\]

---

**Step 2: Pooled Conversion Rate**

Used to estimate variance assuming no true difference:

\\[
p = \\frac{Conversions_A + Conversions_B}{Visitors_A + Visitors_B}
\\]

---

**Step 3: Standard Error**

\\[
SE = \\sqrt{p(1-p) \\left(\\frac{1}{Visitors_A} + \\frac{1}{Visitors_B}\\right)}
\\]

---

**Step 4: Z-score**

\\[
Z = \\frac{CR_B - CR_A}{SE}
\\]

---

**Step 5: P-value**

- Two-tailed test checks for **any difference**
- One-tailed test checks for **improvement only**

The p-value measures how likely this difference is if there were no real effect.

---

**Step 6: Confidence Interval**

\\[
(CR_B - CR_A) \\pm 1.96 \\times SE
\\]

If the interval does not include 0, the result is statistically significant.
            """)

# =================================================
# TAB 2 — BAYESIAN A/B TEST
# =================================================
with tab2:
    st.subheader("Bayesian A/B Test")

    st.write(
        "This approach estimates the **probability that Variant B is better "
        "than Variant A**, which is often more intuitive."
    )

    col1, col2 = st.columns(2)

    with col1:
        visitors_a = st.number_input("Visitors A", min_value=1, value=10000, key="ba")
        conversions_a = st.number_input("Conversions A", min_value=0, value=500, key="ca")

    with col2:
        visitors_b = st.number_input("Visitors B", min_value=1, value=9800, key="bb")
        conversions_b = st.number_input("Conversions B", min_value=0, value=560, key="cb")

    if st.button("Run Bayesian Analysis", type="primary"):
        alpha_a, beta_a = conversions_a + 1, visitors_a - conversions_a + 1
        alpha_b, beta_b = conversions_b + 1, visitors_b - conversions_b + 1

        samples = 100000
        samples_a = beta.rvs(alpha_a, beta_a, size=samples)
        samples_b = beta.rvs(alpha_b, beta_b, size=samples)

        prob_b_better = (samples_b > samples_a).mean()

        st.divider()
        st.metric("Probability B > A", f"{prob_b_better*100:.2f}%")

        with st.expander("What does this mean?"):
            st.write(
                "This tells you how confident you can be that Variant B "
                "outperforms Variant A. For example, 97% means B is better "
                "in 97 out of 100 plausible scenarios."
            )

        with st.expander("How is this calculated? (Math & Logic)"):
            st.markdown("""
Each variant's conversion rate is modeled as a **Beta distribution**.

**Posterior Distribution:**

\\[
Beta(Conversions + 1, Visitors - Conversions + 1)
\\]

We then:
1. Draw many random samples from both distributions
2. Count how often B > A
3. Convert this into a probability

This directly answers the question:
**“How likely is B better than A?”**
            """)

# =================================================
# TAB 3 — SAMPLE SIZE
# =================================================
with tab3:
    st.subheader("Sample Size Calculator")

    st.write(
        "Estimate how many users you need **before running an experiment** "
        "to detect a meaningful improvement."
    )

    baseline = st.number_input(
        "Baseline conversion rate (%)", value=5.0
    ) / 100

    mde = st.number_input(
        "Minimum detectable effect (%)", value=10.0
    ) / 100

    confidence = st.selectbox("Confidence level", [90, 95, 99], index=1)
    power = st.selectbox("Statistical power", [80, 90], index=0)

    if st.button("Calculate Sample Size", type="primary"):
        alpha = 1 - confidence / 100
        beta_val = 1 - power / 100

        z_alpha = norm.ppf(1 - alpha / 2)
        z_beta = norm.ppf(1 - beta_val)

        p1 = baseline
        p2 = baseline * (1 + mde)

        pooled = (p1 + p2) / 2

        n = (
            2 * pooled * (1 - pooled) *
            ((z_alpha + z_beta) ** 2)
        ) / ((p2 - p1) ** 2)

        st.metric("Users per variant", f"{math.ceil(n):,}")

        with st.expander("What does this mean?"):
            st.write(
                "If you run the experiment with fewer users than this, "
                "you risk missing real improvements or drawing incorrect conclusions."
            )

        with st.expander("How is this calculated? (Math & Logic)"):
            st.markdown("""
The formula balances:
- Expected improvement (MDE)
- Natural randomness in conversions
- Desired confidence and power

\\[
n = \\frac{2p(1-p)(Z_{\\alpha} + Z_{\\beta})^2}{(p_2 - p_1)^2}
\\]

Where:
- \\(Z_{\\alpha}\\): confidence
- \\(Z_{\\beta}\\): statistical power
- \\(p_1, p_2\\): baseline and improved rates
            """)

# -------------------------------------------------
# Footer
# -------------------------------------------------
st.divider()
st.caption("YourAnalyst • Practical analytics for confident decisions")
