import streamlit as st
import math
import pandas as pd
import altair as alt
from scipy.stats import norm, beta

# =================================================
# Page Configuration
# =================================================
st.set_page_config(
    page_title="YourAnalyst • A/B Testing Toolkit",
    layout="centered"
)

# =================================================
# Apple-style Minimal Theme
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
.badge {
    padding: 12px 18px;
    border-radius: 999px;
    font-weight: 600;
    display: inline-block;
}
.ship { background-color: #e6f4ea; color: #137333; }
.iterate { background-color: #fff7e6; color: #b06000; }
.stop { background-color: #fdecea; color: #b3261e; }
</style>
""", unsafe_allow_html=True)

# =================================================
# Header
# =================================================
st.title("YourAnalyst A/B Testing Toolkit")
st.caption("From statistical results to confident product decisions")

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

        lift = (cr_b - cr_a)
        lift_pct = lift / cr_a * 100

        ci_low = lift - 1.96 * se
        ci_high = lift + 1.96 * se

        st.divider()
        st.subheader("Key Metrics")

        m1, m2, m3 = st.columns(3)
        m1.metric("CR A", f"{cr_a*100:.2f}%")
        m2.metric("CR B", f"{cr_b*100:.2f}%")
        m3.metric("Lift", f"{lift_pct:.2f}%")

        st.write(f"**P-value:** {p_value:.4f}")
        st.write(
            f"**95% Confidence Interval (Lift):** "
            f"[{ci_low*100:.2f}%, {ci_high*100:.2f}%]"
        )

        # =================================================
        # DECISION BADGE
        # =================================================
        st.subheader("Decision Recommendation")

        if ci_low > 0 and p_value < 0.05:
            st.markdown(
                '<span class="badge ship">SHIP</span>',
                unsafe_allow_html=True
            )
            decision_text = (
                "Strong evidence of improvement. "
                "The lift is statistically significant and consistently positive."
            )
        elif ci_high > 0:
            st.markdown(
                '<span class="badge iterate">ITERATE</span>',
                unsafe_allow_html=True
            )
            decision_text = (
                "Promising direction, but not conclusive. "
                "Consider running longer or refining the variant."
            )
        else:
            st.markdown(
                '<span class="badge stop">STOP</span>',
                unsafe_allow_html=True
            )
            decision_text = (
                "No evidence of improvement. "
                "Variant B does not outperform the control."
            )

        st.write(decision_text)

        # =================================================
        # VISUAL CONFIDENCE INTERVAL CHART
        # =================================================
        st.subheader("Visual Confidence Interval")

        df_ci = pd.DataFrame({
            "metric": ["Lift"],
            "low": [ci_low * 100],
            "high": [ci_high * 100],
            "mean": [lift_pct]
        })

        base = alt.Chart(df_ci).encode(
            y=alt.Y("metric:N", title="")
        )

        ci_bar = base.mark_rule(strokeWidth=6).encode(
            x=alt.X("low:Q", title="Lift (%)"),
            x2="high:Q"
        )

        point = base.mark_point(
            filled=True, size=120, color="#ff5a36"
        ).encode(
            x="mean:Q"
        )

        zero_line = alt.Chart(
            pd.DataFrame({"x": [0]})
        ).mark_rule(
            strokeDash=[4, 4], color="gray"
        ).encode(
            x="x:Q"
        )

        st.altair_chart(
            ci_bar + point + zero_line,
            use_container_width=True
        )

        # =================================================
        # EXPLANATIONS
        # =================================================
        with st.expander("What does this mean?"):
            st.write(
                "The chart shows the range of plausible values for the true lift. "
                "If the entire bar lies to the right of zero, the improvement is "
                "statistically reliable."
            )

        with st.expander("How is this calculated? (Math & Logic)"):
            st.latex(r"CR_A = \frac{Conversions_A}{Visitors_A}")
            st.latex(r"CR_B = \frac{Conversions_B}{Visitors_B}")
            st.latex(r"Z = \frac{CR_B - CR_A}{SE}")
            st.latex(r"(CR_B - CR_A) \pm 1.96 \times SE")

# =================================================
# TAB 2 — BAYESIAN A/B TEST
# =================================================
with tab2:
    st.subheader("Bayesian A/B Test")

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

        st.metric("Probability B > A", f"{prob_b_better*100:.2f}%")

        with st.expander("What does this mean?"):
            st.write(
                "This is the probability that Variant B truly performs better "
                "than Variant A, given the observed data."
            )

# =================================================
# TAB 3 — SAMPLE SIZE
# =================================================
with tab3:
    st.subheader("Sample Size Calculator")

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

# =================================================
# Footer
# =================================================
st.divider()
st.caption("YourAnalyst • Turning data into decisions")
st.caption("Developed by Chandra Sekhar • © 2025")