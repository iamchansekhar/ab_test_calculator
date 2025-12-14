import streamlit as st
import math
from scipy.stats import norm, beta

# =================================================
# Page Configuration
# =================================================
st.set_page_config(
    page_title="YourAnalyst • A/B Testing Toolkit",
    layout="centered"
)

# =================================================
# Apple-style Minimal Theme (Reddish-Orange)
# =================================================
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

# =================================================
# Branding Header
# =================================================
st.title("YourAnalyst A/B Testing Toolkit")
st.caption("Clear experimentation insights for confident product decisions")

st.divider()

# =================================================
# Tabs
# =================================================
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
        "Use this test to determine whether the observed difference between "
        "two variants is **real or likely caused by random chance**."
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

        # -------- Plain English --------
        with st.expander("What does this mean?"):
            if p_value < 0.05:
                st.write(
                    "The improvement seen in Variant B is unlikely to be due to "
                    "random chance. You can be reasonably confident that Variant B "
                    "is performing better than Variant A."
                )
            else:
                st.write(
                    "The observed difference may be due to randomness. "
                    "There is not enough evidence yet to confidently choose Variant B."
                )

        # -------- Mathematical Explanation --------
        with st.expander("How is this calculated? (Math & Logic)"):

            st.write("**Step 1: Conversion Rates**")
            st.latex(r"CR_A = \frac{Conversions_A}{Visitors_A}")
            st.latex(r"CR_B = \frac{Conversions_B}{Visitors_B}")

            st.write("**Step 2: Pooled Conversion Rate**")
            st.latex(r"""
            p = \frac{Conversions_A + Conversions_B}
                     {Visitors_A + Visitors_B}
            """)

            st.write("**Step 3: Standard Error**")
            st.latex(r"""
            SE = \sqrt{
                p(1 - p)
                \left(
                    \frac{1}{Visitors_A}
                    +
                    \frac{1}{Visitors_B}
                \right)
            }
            """)

            st.write("**Step 4: Z-score**")
            st.latex(r"Z = \frac{CR_B - CR_A}{SE}")

            st.write("**Step 5: P-value**")
            st.latex(r"""
            p\text{-value} =
            \begin{cases}
            2(1 - \Phi(|Z|)) & \text{Two-tailed} \\
            1 - \Phi(Z) & \text{One-tailed}
            \end{cases}
            """)

            st.write("**Step 6: Confidence Interval**")
            st.latex(r"(CR_B - CR_A) \pm 1.96 \times SE")

# =================================================
# TAB 2 — BAYESIAN A/B TEST
# =================================================
with tab2:
    st.subheader("Bayesian A/B Test")

    st.write(
        "This method estimates the **probability that Variant B is better "
        "than Variant A**, which is often easier to interpret."
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
                "This represents how confident you can be that Variant B "
                "outperforms Variant A. For example, 96% means B is better "
                "in 96 out of 100 plausible scenarios."
            )

        with st.expander("How is this calculated? (Math & Logic)"):
            st.latex(r"\theta \sim \text{Beta}(\alpha, \beta)")
            st.latex(r"\alpha = Conversions + 1")
            st.latex(r"\beta = Visitors - Conversions + 1")
            st.latex(r"P(\theta_B > \theta_A)")

# =================================================
# TAB 3 — SAMPLE SIZE CALCULATOR
# =================================================
with tab3:
    st.subheader("Sample Size Calculator")

    st.write(
        "Estimate how many users you need **before running an experiment** "
        "to reliably detect a meaningful improvement."
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
                "Running an experiment with fewer users than this "
                "makes it likely that you miss real improvements or "
                "draw incorrect conclusions."
            )

        with st.expander("How is this calculated? (Math & Logic)"):
            st.latex(r"""
            n =
            \frac{
                2 \cdot p(1 - p) \cdot (Z_{\alpha} + Z_{\beta})^2
            }{
                (p_2 - p_1)^2
            }
            """)
            st.latex(r"p = \frac{p_1 + p_2}{2}")

# =================================================
# Footer
# =================================================
st.divider()
st.caption("YourAnalyst • Practical analytics, explained clearly")
