
import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="India AQI Dashboard",
    page_icon="🌍",
    layout="wide"
)

@st.cache_data
def load_data():
    # Check for cleaned dataset or fall back to raw city_day.csv
    possible_paths = [
        "cleaned_aqi.csv",
        os.path.join("data", "cleaned_aqi.csv"),
        "city_day.csv",
        os.path.join("data", "city_day.csv")
    ]
    file_path = None
    for path in possible_paths:
        if os.path.exists(path):
            file_path = path
            break

    if file_path is None:
        st.error("Error: Could not find 'cleaned_aqi.csv' or 'data/city_day.csv'. Please check your project folder.")
        st.stop()

    df = pd.read_csv(file_path)

    # Ensure numeric types for core pollutants
    pollutant_cols = ['PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'O3', 'AQI']
    for col in pollutant_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    return df

df = load_data()

st.title("🌍 India Air Quality Index (AQI) Dashboard")
st.write("CUTM1018 | Interactive City Pollutant Assessment & Air Quality Analysis")

# Display full dataset overview
st.subheader("📋 Dataset Preview")
st.dataframe(df.head(10), use_container_width=True)

st.sidebar.header("🔍 Filter Options")

# Retrieve sorted unique city list
available_cities = sorted(df['City'].dropna().unique().tolist()) if 'City' in df.columns else []

# Select City dropdown in sidebar
selected_city = st.sidebar.selectbox(
    "Select City",
    ["All Cities"] + available_cities
)

# Optional pollutant filter for detailed comparison
pollutant_list = [p for p in ['PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'O3'] if p in df.columns]
selected_pollutant = st.sidebar.selectbox(
    "Select Primary Pollutant for Inspection",
    pollutant_list,
    index=0
)

if selected_city != "All Cities":
    filtered_df = df[df["City"] == selected_city].copy()
else:
    filtered_df = df.copy()

st.subheader("📈 Key Summary Statistics")

col1, col2, col3, col4 = st.columns(4)

# Metric 1: Record count
col1.metric(
    label="Monitored Days / Records",
    value=f"{len(filtered_df):,}"
)

# Metric 2: Average AQI
avg_aqi = filtered_df["AQI"].mean() if "AQI" in filtered_df.columns else 0
col2.metric(
    label="Average AQI",
    value=f"{round(avg_aqi, 2)}" if not pd.isna(avg_aqi) else "N/A"
)

# Metric 3: Highest Recorded AQI
max_aqi = filtered_df["AQI"].max() if "AQI" in filtered_df.columns else 0
col3.metric(
    label="Peak AQI Recorded",
    value=f"{round(max_aqi, 1)}" if not pd.isna(max_aqi) else "N/A"
)

# Metric 4: Mean Selected Pollutant Concentration
avg_pollutant = filtered_df[selected_pollutant].mean() if selected_pollutant in filtered_df.columns else 0
col4.metric(
    label=f"Mean {selected_pollutant} (µg/m³)",
    value=f"{round(avg_pollutant, 2)}" if not pd.isna(avg_pollutant) else "N/A"
)

st.divider()

st.subheader("📊 Visual Analytics")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown(f"### Mean Pollutants in {selected_city}")
    # Compute mean for each available pollutant
    eval_pollutants = [p for p in pollutant_list if p in filtered_df.columns]
    avg_values = [filtered_df[p].mean() for p in eval_pollutants]

    fig1, ax1 = plt.subplots(figsize=(6, 4.2))
    bars = ax1.bar(eval_pollutants, avg_values, color=['#e63946', '#f4a261', '#e76f51', '#2a9d8f', '#264653', '#8338ec'][:len(eval_pollutants)])
    ax1.set_xlabel("Pollutant Type", fontweight='bold')
    ax1.set_ylabel("Mean Concentration (µg/m³)", fontweight='bold')
    ax1.set_title(f"Pollutant Profile: {selected_city}", fontsize=11, fontweight='bold')
    ax1.grid(axis='y', linestyle='--', alpha=0.6)

    # Add numeric labels on top of bars
    for bar in bars:
        height = bar.get_height()
        if not pd.isna(height):
            ax1.annotate(f"{height:.1f}",
                         xy=(bar.get_x() + bar.get_width() / 2, height),
                         xytext=(0, 3),
                         textcoords="offset points",
                         ha='center', va='bottom', fontsize=8)

    st.pyplot(fig1)

with chart_col2:
    st.markdown(f"### {selected_pollutant} vs AQI Correlation")
    fig2, ax2 = plt.subplots(figsize=(6, 4.2))

    # Scatter distribution
    ax2.scatter(
        filtered_df[selected_pollutant],
        filtered_df['AQI'],
        alpha=0.35,
        color="#1d3557",
        edgecolors='none'
    )
    ax2.set_xlabel(f"{selected_pollutant} (µg/m³)", fontweight='bold')
    ax2.set_ylabel("Composite AQI", fontweight='bold')
    ax2.set_title(f"{selected_pollutant} vs. AQI in {selected_city}", fontsize=11, fontweight='bold')
    ax2.grid(True, linestyle='--', alpha=0.5)

    st.pyplot(fig2)

st.subheader("📑 Filtered Observation Records")
st.dataframe(filtered_df, use_container_width=True)
