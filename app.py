
import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Healthcare Metrics Dashboard",
    page_icon="🏥",
    layout="wide"
)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

DATA_FOLDER = "healthcare_dashboard"

@st.cache_data
def load_data():
    metrics = pd.read_csv(
        os.path.join(DATA_FOLDER, "overall_metrics.csv")
    )

    metrics = metrics.rename(columns={
        "Unnamed: 0": "Metric",
        "0": "Value"
    })

    states = pd.read_csv(
        os.path.join(DATA_FOLDER, "state_summary.csv")
    )

    facilities = pd.read_csv(
        os.path.join(DATA_FOLDER, "facility_summary.csv")
    )

    return metrics, states, facilities


metrics, states, facilities = load_data()
# --------------------------------------------------
# HELPER FUNCTION FOR METRICS
# --------------------------------------------------
@st.cache_data
def load_data():
    metrics = pd.read_csv(
        os.path.join(DATA_FOLDER, "overall_metrics.csv")
    )

    metrics = metrics.rename(columns={
        "Unnamed: 0": "Metric",
        "0": "Value"
    })

    states = pd.read_csv(
        os.path.join(DATA_FOLDER, "state_summary.csv")
    )

    facilities = pd.read_csv(
        os.path.join(DATA_FOLDER, "facility_summary.csv")
    )

    return metrics, states, facilities

# --------------------------------------------------
# HELPER FUNCTION FOR METRICS
# --------------------------------------------------

def get_metric(name):
    result = metrics.loc[
        metrics["Metric"] == name, "Value"
    ]

    if result.empty:
        return None

    return pd.to_numeric(result.iloc[0], errors="coerce")

# --------------------------------------------------
# DASHBOARD HEADER
# --------------------------------------------------

st.title("🏥 Healthcare Metrics Dashboard")

st.subheader("Q2 2024 PBJ Daily Nurse Staffing Analysis")

st.caption(
    "Management dashboard analyzing nursing facility staffing "
    "patterns across the United States."
)

st.divider()

# --------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------

page = st.sidebar.radio(
    "Dashboard Navigation",
    [
        "Overview",
        "State Comparisons",
        "Facility Analysis",
        "Data Quality"
    ]
)

# --------------------------------------------------
# PAGE 1: OVERVIEW
# --------------------------------------------------

if page == "Overview":

    st.header("Overall Staffing Performance")

    facilities_count = states["Number_of_Facilities"].sum()

    resident_days = states["Total_Resident_Days"].sum()

    direct_care_per_resident = get_metric(
        "Average Direct-Care Hours Per Resident"
    )

    contract_percentage = get_metric(
        "Average Contract Staffing Percentage"
    )

    total_direct_care_hours = get_metric(
        "Total Direct-Care Hours in Q2"
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Number of Facilities", f"{facilities_count:,.0f}")
    col2.metric("Total Resident-Days", f"{resident_days:,.0f}")
    col3.metric(
        "Average Direct-Care Hours Per Resident",
        f"{direct_care_per_resident:.2f}"
    )
    col4.metric(
        "Contract Staffing",
        f"{contract_percentage:.2f}%"
    )
    col5.metric(
        "Total Direct-Care Hours",
        f"{total_direct_care_hours:,.0f}"
    )
    st.divider()

    st.subheader("Project Summary")

    st.write(
        """
        This dashboard examines daily nurse staffing data from
        14,564 nursing facilities during the second quarter of 2024.

        The analysis evaluates:

        - Direct-care staffing hours per resident-day
        - Differences in staffing across states
        - Facility-level staffing patterns
        - Contract staffing utilization
        - Potential data-quality concerns
        """
    )

# --------------------------------------------------
# PAGE 2: STATE COMPARISONS
# --------------------------------------------------

elif page == "State Comparisons":

    st.header("State Staffing Comparisons")

    required = [
        "STATE",
        "Hours_Per_Resident_Day",
        "Contract_Staffing_Percentage"
    ]

    missing = [c for c in required if c not in states.columns]

    if missing:
        st.error(f"Missing state columns: {missing}")
        st.stop()

    states["Hours_Per_Resident_Day"] = pd.to_numeric(
        states["Hours_Per_Resident_Day"], errors="coerce"
    )

    states["Contract_Staffing_Percentage"] = pd.to_numeric(
        states["Contract_Staffing_Percentage"], errors="coerce"
    )

    st.subheader("Highest Staffing Levels")

    top_states = states.nlargest(
        10, "Hours_Per_Resident_Day"
    ).sort_values("Hours_Per_Resident_Day")

    fig = px.bar(
        top_states,
        x="Hours_Per_Resident_Day",
        y="STATE",
        orientation="h",
        title="Top 10 States by Direct-Care Hours Per Resident-Day",
        labels={
            "Hours_Per_Resident_Day": "Hours Per Resident-Day",
            "STATE": "State"
        }
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Lowest Staffing Levels")

    bottom_states = states.nsmallest(
        10, "Hours_Per_Resident_Day"
    ).sort_values("Hours_Per_Resident_Day")

    fig = px.bar(
        bottom_states,
        x="Hours_Per_Resident_Day",
        y="STATE",
        orientation="h",
        title="Bottom 10 States by Direct-Care Hours Per Resident-Day",
        labels={
            "Hours_Per_Resident_Day": "Hours Per Resident-Day",
            "STATE": "State"
        }
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Contract Staffing by State")

    contract_states = states.sort_values(
        "Contract_Staffing_Percentage",
        ascending=False
    )

    fig = px.bar(
        contract_states,
        x="STATE",
        y="Contract_Staffing_Percentage",
        title="Contract Staffing Percentage by State",
        labels={
            "Contract_Staffing_Percentage": "Contract Staffing (%)",
            "STATE": "State"
        }
    )

    st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------
# PAGE 3: FACILITY ANALYSIS
# --------------------------------------------------

elif page == "Facility Analysis":

    st.header("Facility-Level Analysis")

    required = [
        "PROVNUM",
        "PROVNAME",
        "STATE",
        "Hours_Per_Resident_Day",
        "Zero_Staffing_Percentage"
    ]

    missing = [c for c in required if c not in facilities.columns]

    if missing:
        st.error(f"Missing facility columns: {missing}")
        st.stop()

    selected_state = st.selectbox(
        "Select a State",
        ["All States"] + sorted(
            facilities["STATE"].dropna().unique().tolist()
        )
    )

    filtered = facilities.copy()

    if selected_state != "All States":
        filtered = filtered[
            filtered["STATE"] == selected_state
        ]

    search = st.text_input("Search Facility Name or Provider ID")

    if search:
        filtered = filtered[
            filtered["PROVNAME"].astype(str).str.contains(
                search, case=False, na=False
            ) |
            filtered["PROVNUM"].astype(str).str.contains(
                search, case=False, na=False
            )
        ]

    st.write(f"Facilities displayed: {len(filtered):,}")

    st.dataframe(
        filtered.sort_values(
            "Hours_Per_Resident_Day",
            ascending=True
        ),
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Lowest Staffing Facilities")

    lowest = filtered.nsmallest(
        15, "Hours_Per_Resident_Day"
    )

    st.dataframe(
        lowest,
        use_container_width=True,
        hide_index=True
    )

# --------------------------------------------------
# PAGE 4: DATA QUALITY
# --------------------------------------------------

elif page == "Data Quality":

    st.header("Data Quality and Reporting Flags")

    required = [
        "Zero_Staffing_Days",
        "Positive_Census_Days",
        "Zero_Staffing_Percentage"
    ]

    missing = [c for c in required if c not in facilities.columns]

    if missing:
        st.error(f"Missing facility columns: {missing}")
        st.stop()

    facilities["Zero_Staffing_Percentage"] = pd.to_numeric(
        facilities["Zero_Staffing_Percentage"],
        errors="coerce"
    )

    facilities["Zero_Staffing_Days"] = pd.to_numeric(
        facilities["Zero_Staffing_Days"],
        errors="coerce"
    )

    flagged = facilities[
        facilities["Zero_Staffing_Days"] > 0
    ].copy()

    col1, col2 = st.columns(2)

    col1.metric(
        "Facilities With Zero-Staffing Days",
        f"{len(flagged):,}"
    )

    col2.metric(
        "Total Zero-Staffing Days",
        f"{facilities['Zero_Staffing_Days'].sum():,.0f}"
    )

    st.subheader("Facilities With Zero-Staffing Days")

    st.dataframe(
        flagged.sort_values(
            "Zero_Staffing_Percentage",
            ascending=False
        ),
        use_container_width=True,
        hide_index=True
    )

    st.info(
        "Zero reported staffing hours are data-quality flags, "
        "not proof that no care was provided."
    )

    st.caption(
        "Note: Contract staffing is not a measure of overtime. "
        "This dataset does not contain an explicit overtime field."
    )

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "Healthcare Metrics Project | Q2 2024 | "
    "PBJ Daily Nurse Staffing Data"
)
