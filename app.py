import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.style.use("dark_background")

st.set_page_config(page_title="Decision Lab", layout="centered")

st.title("Decision Lab")
st.subheader("Modeling subjective decisions under uncertainty")
st.caption("A hybrid decision framework: probability, impact, and emotional weight.")

decision = st.text_input("What decision are you evaluating?")

st.markdown("### Define Possible Outcomes")

n_outcomes = st.slider("Number of scenarios", 1, 5, 3)

data = []

for i in range(n_outcomes):
    st.markdown(f"#### Scenario {i+1}")
    col1, col2, col3 = st.columns(3)

    with col1:
        name = st.text_input(f"Outcome name {i+1}", key=f"name_{i}")

    with col2:
        prob = st.number_input(f"Probability {i+1}", min_value=0.0, max_value=1.0, step=0.01, key=f"prob_{i}")

    with col3:
        impact = st.number_input(f"Emotional Impact (-10 to 10) {i+1}", min_value=-10.0, max_value=10.0, step=0.5, key=f"impact_{i}")

    data.append((name, prob, impact))

if st.button("Analyze Decision"):

    df = pd.DataFrame(data, columns=["Outcome", "Probability", "Impact"])

    total_prob = df["Probability"].sum()

    if abs(total_prob - 1.0) > 0.001:
        st.error(f"Probabilities must sum to 1. Current total: {round(total_prob,3)}")
    else:
        # Core calculations
        expected_value = np.sum(df["Probability"] * df["Impact"])
        variance = np.sum(df["Probability"] * (df["Impact"] - expected_value)**2)
        std_dev = np.sqrt(variance)

        # =========================
        # Decision Overview
        # =========================

        st.markdown("## Decision Overview")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Expected Value", round(expected_value, 3))

        with col2:
            st.metric("Risk (Std Deviation)", round(std_dev, 3))

        # =========================
        # Emotional Weighted Index
        # =========================

        ewi = expected_value / (1 + std_dev)

        st.markdown("## Emotional-Weighted Index")

        st.metric("EWI Score", round(ewi, 3))

        if ewi > 1:
            signal = "Strong Strategic Alignment"
        elif ewi > 0:
            signal = "Positive but Risk-Sensitive"
        elif ewi > -0.5:
            signal = "Fragile / Emotionally Volatile"
        else:
            signal = "Misaligned Decision"

        st.success(f"Signal: {signal}")

        # =========================
        # Interpretation
        # =========================

        st.markdown("## Interpretation")

        if expected_value > 0:
            direction = "positive"
        else:
            direction = "negative"

        if std_dev < abs(expected_value) * 0.5:
            risk_profile = "low volatility"
        elif std_dev < abs(expected_value):
            risk_profile = "moderate volatility"
        else:
            risk_profile = "high volatility"

        if expected_value > 0 and risk_profile == "low volatility":
            strategic_note = "This is a structurally attractive decision."
        elif expected_value > 0:
            strategic_note = "The upside exists, but variability is meaningful."
        elif expected_value <= 0 and risk_profile == "high volatility":
            strategic_note = "This scenario carries downside asymmetry."
        else:
            strategic_note = "The outcome balance requires cautious evaluation."

        st.info(
            f"""
**Decision Signal:** {direction.upper()}  

**Volatility Profile:** {risk_profile}  

**Strategic Interpretation:**  
{strategic_note}
"""
        )

        # =========================
        # Outcome Impact Chart
        # =========================

        fig, ax = plt.subplots()

        colors = ["#54A24B" if x >= 0 else "#E45756" for x in df["Impact"]]

        ax.bar(df["Outcome"], df["Impact"], color=colors)
        ax.axhline(0, color="white", linewidth=1)
        ax.set_ylabel("Impact")
        ax.set_title("Outcome Impact Distribution")
        ax.grid(axis="y", alpha=0.15)

        st.pyplot(fig)

        # =========================
        # Monte Carlo Simulation
        # =========================

        st.markdown("## Risk Simulation")

        simulations = 10000
        outcomes = df["Impact"].values
        probabilities = df["Probability"].values

        simulated_results = np.random.choice(
            outcomes,
            size=simulations,
            p=probabilities
        )

        simulated_mean = np.mean(simulated_results)

        st.metric("Simulated Mean", round(simulated_mean, 3))

        fig2, ax2 = plt.subplots()

        ax2.hist(
            simulated_results,
            bins=30,
            color="#4C78A8",
            edgecolor="white",
            alpha=0.85
        )

        ax2.axvline(
            simulated_mean,
            color="#F58518",
            linestyle="--",
            linewidth=2
        )

        ax2.set_title("Monte Carlo Distribution")
        ax2.set_xlabel("Impact")
        ax2.set_ylabel("Frequency")
        ax2.grid(alpha=0.15)

        st.pyplot(fig2)
