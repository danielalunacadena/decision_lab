import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.style.use("dark_background")

presets = {
    "Career Decision": [
        ("Career Growth", 0.4, 9),
        ("Stable Transition", 0.3, 3),
        ("Regret / Instability", 0.3, -6)
    ],
    "Startup Launch": [
        ("High Success", 0.25, 10),
        ("Moderate Traction", 0.35, 5),
        ("Failure", 0.40, -8)
    ],
    "Relationship Decision": [
        ("Positive Outcome", 0.3, 8),
        ("Same Patterns", 0.4, -5),
        ("Emotional Chaos", 0.3, -9)
    ],
    "Investment Risk": [
        ("High Return", 0.2, 10),
        ("Moderate Return", 0.5, 4),
        ("Loss", 0.3, -6)
    ]
}

st.set_page_config(page_title="Decision Lab", layout="centered")

st.title("Decision Lab")

scenario = st.selectbox(
    "Choose a decision scenario",
    ["Custom"] + list(presets.keys())
)
st.subheader("Modeling subjective decisions under uncertainty")
st.caption("A hybrid decision framework: probability, impact, and emotional weight.")

decision = st.text_input("What decision are you evaluating?")

st.markdown("### Define Possible Outcomes")

if scenario == "Custom":
    n_outcomes = st.slider("Number of scenarios", 1, 5, 3)
    preset_data = None
else:
    preset_data = presets[scenario]
    n_outcomes = len(preset_data)
    st.info(f"Preset loaded: {scenario}")

if preset_data:
    for i in range(n_outcomes):
        if f"name_{i}" not in st.session_state:
            st.session_state[f"name_{i}"] = preset_data[i][0]
            st.session_state[f"prob_{i}"] = float(preset_data[i][1])
            st.session_state[f"impact_{i}"] = float(preset_data[i][2])

data = []

if "last_scenario" not in st.session_state:
    st.session_state.last_scenario = scenario

if st.session_state.last_scenario != scenario:
    for key in list(st.session_state.keys()):
        if key.startswith("name_") or key.startswith("prob_") or key.startswith("impact_"):
            del st.session_state[key]

    st.session_state.last_scenario = scenario
    st.rerun()

for i in range(n_outcomes):
    st.markdown(f"#### Scenario {i+1}")
    col1, col2, col3 = st.columns(3)

    with col1:
        name = st.text_input(
            f"Outcome name {i+1}",
            key=f"name_{i}"
        )

    with col2:
        default_prob = preset_data[i][1] if preset_data else 0.0
        prob = st.number_input(
            f"Probability {i+1}",
            min_value=0.0,
            max_value=1.0,
            step=0.01,
            key=f"prob_{i}"
        )

    with col3:
        default_impact = preset_data[i][2] if preset_data else 0.0
        impact = st.number_input(
            f"Emotional Impact (-10 to 10) {i+1}",
            min_value=-10.0,
            max_value=10.0,
            step=0.5,
            key=f"impact_{i}"
        )

    data.append((name, prob, impact))

if st.button("Analyze Decision"):

    df = pd.DataFrame(data, columns=["Outcome", "Probability", "Impact"])
    total_prob = df["Probability"].sum()

    if abs(total_prob - 1.0) > 0.001:
        st.error(f"Probabilities must sum to 1. Current total: {round(total_prob,3)}")

    else:
        # =========================
        # Core calculations
        # =========================
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

        # =========================
        # Decision Insight
        # =========================
        st.markdown("## Decision Insight")

        if expected_value > 2 and std_dev < 3:
            st.success("Strong positive decision. High upside with manageable risk.")
        elif expected_value > 0 and std_dev < 5:
            st.info("Positive decision, but consider variability.")
        elif expected_value > 0 and std_dev >= 5:
            st.warning("Upside exists, but risk is high.")
        elif expected_value <= 0 and std_dev < 3:
            st.warning("Low return. Stable but not attractive.")
        else:
            st.error("High risk with negative expectation.")

        # =========================
        # Signal
        # =========================
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

        direction = "positive" if expected_value > 0 else "negative"

        if std_dev < abs(expected_value) * 0.5:
            risk_profile = "low volatility"
        elif std_dev < abs(expected_value):
            risk_profile = "moderate volatility"
        else:
            risk_profile = "high volatility"

        if expected_value > 0 and risk_profile == "low volatility":
            strategic_note = "Structurally attractive decision."
        elif expected_value > 0:
            strategic_note = "Upside exists but with variability."
        elif expected_value <= 0 and risk_profile == "high volatility":
            strategic_note = "Downside risk dominates."
        else:
            strategic_note = "Requires cautious evaluation."

        st.info(f"""
**Decision Signal:** {direction.upper()}  
**Volatility Profile:** {risk_profile}  
**Strategic Interpretation:** {strategic_note}
""")

        # =========================
        # Recommendation
        # =========================
        st.markdown("## Recommendation")

        if ewi > 1:
            recommendation = "You should strongly pursue this decision. It aligns well with both logic and emotional payoff."
        elif ewi > 0:
            recommendation = "This decision is favorable, but with some uncertainty."
        elif ewi > -0.5:
            recommendation = "This is a fragile decision. Consider gathering more information."
        else:
            recommendation = "This decision may not be advisable."

        st.markdown(f"### 💡 {recommendation}")

        # =========================
        # Chart
        # =========================
        fig, ax = plt.subplots()

        colors = ["#54A24B" if x >= 0 else "#E45756" for x in df["Impact"]]

        ax.bar(df["Outcome"], df["Impact"], color=colors)
        ax.axhline(0, color="white")
        ax.set_title("Outcome Impact")

        st.pyplot(fig)

        # =========================
        # Monte Carlo
        # =========================
        st.markdown("## Risk Simulation")

        simulated = np.random.choice(
            df["Impact"],
            size=10000,
            p=df["Probability"]
        )

        st.metric("Simulated Mean", round(np.mean(simulated), 3))

        fig2, ax2 = plt.subplots()
        ax2.hist(simulated, bins=30)
        st.pyplot(fig2)