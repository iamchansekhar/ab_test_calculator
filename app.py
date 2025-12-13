
import streamlit as st
import math
from scipy.stats import norm

st.set_page_config(
    page_title="A/B Test Calculator | YourAnalyst",
    layout="centered"
)

st.title("A/B Testing Calculator")
st.caption("Free product analytics tools by **YourAnalyst**")

st.divider()

tab1, tab2 = st.tabs(["A/B Test Significance", "Sample Size Calculator"])

with tab1:
    st.subheader("Statistical Significance Calculator")
    st.write(
        "Compare two variants using a two-proportion Z-test to determine "
        "whether the observed lift is statistically significant."
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

    if st.button("Calculate Significance"):
        cr_a = conversions_a / visitors_a
        cr_b = conversions_b / visitors_b

        pooled_cr = (conversions_a + conversions_b) / (visitors_a + visitors_b)
        se = math.sqrt(
            pooled_cr * (1 - pooled_cr) * (1/visitors_a + 1/visitors_b)
        )

        z_score = (cr_b - cr_a) / se
        p_value = 2 * (1 - norm.cdf(abs(z_score)))
        lift = ((cr_b - cr_a) / cr_a) * 100

        st.divider()
        st.subheader("Results")

        m1, m2, m3 = st.columns(3)
        m1.metric("Conversion Rate A", f"{cr_a*100:.2f}%")
        m2.metric("Conversion Rate B", f"{cr_b*100:.2f}%")
        m3.metric("Lift", f"{lift:.2f}%")

        st.write(f"**Z-score:** {z_score:.3f}")
        st.write(f"**P-value:** {p_value:.4f}")

        if p_value < 0.05:
            st.success("Result is statistically significant at 95% confidence")
        else:
            st.warning("Result is NOT statistically significant")

        st.caption(
            "Methodology: Two-proportion Z-test. "
            "Assumes independent samples and sufficiently large sample sizes."
        )

with tab2:
    st.subheader("Sample Size Calculator")
    st.write(
        "Estimate how many users you need per variant before running an experiment."
    )

    baseline_cr = st.number_input(
        "Baseline conversion rate (%)",
        min_value=0.1,
        max_value=100.0,
        value=5.0
    ) / 100

    mde = st.number_input(
        "Minimum detectable effect (relative lift %)",
        min_value=1.0,
        max_value=100.0,
        value=10.0
    ) / 100

    confidence = st.selectbox(
        "Confidence level",
        options=[90, 95, 99],
        index=1
    )

    power = st.selectbox(
        "Statistical power",
        options=[80, 90],
        index=0
    )

    if st.button("Calculate Sample Size"):
        alpha = 1 - confidence / 100
        beta = 1 - power / 100

        z_alpha = norm.ppf(1 - alpha / 2)
        z_beta = norm.ppf(1 - beta)

        p1 = baseline_cr
        p2 = baseline_cr * (1 + mde)

        pooled_p = (p1 + p2) / 2

        sample_size = (
            2 * pooled_p * (1 - pooled_p) *
            ((z_alpha + z_beta) ** 2)
        ) / ((p2 - p1) ** 2)

        st.divider()
        st.subheader("Required Sample Size")

        st.metric(
            "Users per variant",
            f"{math.ceil(sample_size):,}"
        )

        st.caption(
            "Assumes equal traffic split and two-sided hypothesis test."
        )

st.divider()
st.caption(
    "Built with Python & Streamlit. "
    "Use responsibly — statistics are directional, not absolute truth."
)
