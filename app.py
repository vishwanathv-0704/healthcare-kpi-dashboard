
import os
import pandas as pd
import streamlit as st
import plotly.express as px
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="AURORA | Healthcare Intelligence",
    page_icon="🏥",
    layout="wide"
)

# --------------------------------------------------
# AURORA CUSTOM UI THEME
# --------------------------------------------------

st.markdown("""
<style>
.stApp {
    background: #F1F5F7;
    color: #172F40;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1450px;
}

[data-testid="stSidebar"] {
    background: #102638;
}

[data-testid="stSidebar"] * {
    color: #E5EFF4;
}

[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: #1B394D;
    border-color: #365366;
}

h1, h2, h3 {
    color: #102638 !important;
    font-weight: 700 !important;
    letter-spacing: -0.5px;
}

h2 {
    border-left: 4px solid #16A994;
    padding-left: 12px;
}

[data-testid="stMetric"] {
    background: #FFFFFF;
    padding: 20px 22px;
    border-radius: 14px;
    border: 1px solid #E1E9ED;
    box-shadow: 0 3px 12px rgba(16, 38, 56, 0.04);
}

[data-testid="stMetricLabel"] {
    color: #627787 !important;
    font-size: 13px !important;
    font-weight: 600 !important;
}

[data-testid="stMetricValue"] {
    color: #102638 !important;
    font-weight: 750 !important;
}

[data-testid="stPlotlyChart"] {
    background: #FFFFFF;
    padding: 12px;
    border-radius: 14px;
    border: 1px solid #E1E9ED;
    box-shadow: 0 3px 12px rgba(16, 38, 56, 0.04);
}

[data-baseweb="select"] > div {
    border-radius: 9px;
}

[data-testid="stDateInput"] input {
    border-radius: 9px;
}

[data-testid="stAlert"] {
    border-radius: 10px;
}

hr {
    border-color: #DCE6EB;
}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# AURORA HEADER
# IMPORTANT: HTML lines start at column zero.
# --------------------------------------------------

st.markdown("""
<div style="background:linear-gradient(115deg,#102638,#1C4658);padding:28px 32px;border-radius:16px;margin-bottom:25px;">
<div style="color:#4DD5C0;font-size:12px;font-weight:700;letter-spacing:3px;">A U R O R A &nbsp; | &nbsp; HEALTHCARE INTELLIGENCE</div>
<div style="color:#FFFFFF;font-size:32px;font-weight:750;margin-top:12px;">Healthcare Performance Overview</div>
<div style="color:#BDD0DA;font-size:14px;margin-top:8px;">Patient outcomes &nbsp; · &nbsp; Hospital operations &nbsp; · &nbsp; Clinical efficiency</div>
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------

@st.cache_resource
def get_engine():
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "3306")
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "")
    db = os.getenv("DB_NAME", "healthcare_analytics")

    return create_engine(
        f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}"
    )


engine = get_engine()


@st.cache_data(ttl=60)
def read_table(table):
    return pd.read_sql(f"SELECT * FROM {table}", engine)


# --------------------------------------------------
# KPI CONFIGURATION
# --------------------------------------------------

specs = [
    {
        "title": "Patient Satisfaction",
        "monthly_table": "agg_patient_satisfaction",
        "daily_table": "agg_daily_patient_satisfaction",
        "metric": "avg_satisfaction",
        "count": "survey_count",
        "unit": "Average score (out of 5)",
        "type": "weighted"
    },
    {
        "title": "Average Length of Stay",
        "monthly_table": "agg_length_of_stay",
        "daily_table": "agg_daily_length_of_stay",
        "metric": "avg_length_of_stay_days",
        "count": "discharged_admissions",
        "unit": "Days",
        "type": "weighted"
    },
    {
        "title": "Hospital Readmission Rate",
        "monthly_table": "agg_readmission_rate",
        "daily_table": "agg_daily_readmission_rate",
        "metric": "readmission_rate_pct",
        "count": "eligible_discharges",
        "unit": "Percent",
        "type": "readmission"
    },
    {
        "title": "Physician Productivity",
        "monthly_table": "agg_physician_productivity",
        "daily_table": "agg_daily_physician_productivity",
        "metric": "completed_appointments",
        "count": None,
        "unit": "Completed appointments",
        "type": "sum"
    },
    {
        "title": "Patient Wait Time",
        "monthly_table": "agg_patient_wait_time",
        "daily_table": "agg_daily_patient_wait_time",
        "metric": "avg_wait_minutes",
        "count": "appointment_count",
        "unit": "Minutes",
        "type": "weighted"
    }
]


# --------------------------------------------------
# MAIN DASHBOARD
# --------------------------------------------------

try:

    hospitals = read_table("hospitals")

    hospital_options = ["All hospitals"] + hospitals[
        "hospital_name"
    ].tolist()

    selected_hospital = st.sidebar.selectbox(
        "Hospital",
        hospital_options
    )

    period = st.sidebar.selectbox(
        "Select Time Range",
        [
            "Past 1 week",
            "Past 1 month",
            "Past 3 months",
            "Past 6 months",
            "Past 1 year",
            "Past 2 years",
            "Custom range"
        ]
    )

    # Latest date in generated dataset.
    data_end = pd.Timestamp("2026-11-17")

    daily_mode = period in [
        "Past 1 week",
        "Past 1 month"
    ]

    if period == "Past 1 week":

        start_date = data_end - pd.Timedelta(days=6)
        end_date = data_end

    elif period == "Past 1 month":

        start_date = data_end - pd.Timedelta(days=29)
        end_date = data_end

    elif period == "Past 3 months":

        start_date = data_end - pd.DateOffset(months=3)
        end_date = data_end

    elif period == "Past 6 months":

        start_date = data_end - pd.DateOffset(months=6)
        end_date = data_end

    elif period == "Past 1 year":

        start_date = data_end - pd.DateOffset(years=1)
        end_date = data_end

    elif period == "Past 2 years":

        start_date = data_end - pd.DateOffset(years=2)
        end_date = data_end

    else:

        selected_dates = st.sidebar.date_input(
            "Custom Date Range",
            value=(
                pd.Timestamp("2022-01-01").date(),
                data_end.date()
            ),
            min_value=pd.Timestamp("2022-01-01").date(),
            max_value=data_end.date()
        )

        if len(selected_dates) != 2:
            st.info("Please select both dates.")
            st.stop()

        start_date = pd.Timestamp(selected_dates[0])
        end_date = pd.Timestamp(selected_dates[1])

        if start_date > end_date:
            st.error("Start date cannot be after end date.")
            st.stop()

        daily_mode = (
            end_date - start_date
        ).days <= 30

    start_date = pd.Timestamp(start_date).normalize()
    end_date = pd.Timestamp(end_date).normalize()

    # Hospital filter.
    selected_id = None

    if selected_hospital != "All hospitals":

        selected_id = hospitals.loc[
            hospitals["hospital_name"] == selected_hospital,
            "hospital_id"
        ].iloc[0]

    # Select daily or monthly date column.
    if daily_mode:
        date_col = "metric_date"
        chart_label = "Daily Trend"
        xaxis_label = "Date"
    else:
        date_col = "month"
        chart_label = "Monthly Trend"
        xaxis_label = "Month"

    st.caption(
        f"Selected period: {start_date.date()} to {end_date.date()}"
    )

    if daily_mode:
        st.info("Daily view: each point represents one day.")
    else:
        st.info("Monthly view: each point represents one month.")


    # --------------------------------------------------
    # KPI LOOP
    # --------------------------------------------------

    for spec in specs:

        title = spec["title"]
        metric = spec["metric"]
        count_col = spec["count"]

        table = (
            spec["daily_table"]
            if daily_mode
            else spec["monthly_table"]
        )

        df = read_table(table)

        df[date_col] = pd.to_datetime(df[date_col])

        # Date filtering.
        if daily_mode:

            df = df[
                (df[date_col] >= start_date) &
                (df[date_col] <= end_date)
            ]

        else:

            start_month = start_date.to_period("M").to_timestamp()
            end_month = end_date.to_period("M").to_timestamp()

            df = df[
                (df[date_col] >= start_month) &
                (df[date_col] <= end_month)
            ]

        # Hospital filtering.
        if selected_id is not None:
            df = df[df["hospital_id"] == selected_id]

        st.subheader(title)

        if df.empty:

            if title == "Hospital Readmission Rate" and daily_mode:
                st.warning(
                    "Readmission rate is unavailable for this period. "
                    "A complete 30-day follow-up window is required."
                )
            else:
                st.warning(f"No data available for {title}.")

            continue

        # ----------------------------------------------
        # WEIGHTED AVERAGE KPIs
        # ----------------------------------------------

        if spec["type"] == "weighted":

            df["_weighted"] = df[metric] * df[count_col]

            total_count = df[count_col].sum()

            if total_count == 0:
                st.warning(f"No eligible records for {title}.")
                continue

            kpi_value = df["_weighted"].sum() / total_count

            trend = df.groupby(
                date_col, as_index=False
            ).agg(
                weighted=("_weighted", "sum"),
                count=(count_col, "sum")
            )

            trend[metric] = (
                trend["weighted"] / trend["count"]
            )

            if title == "Patient Satisfaction":
                display_value = f"{kpi_value:.2f} / 5"

            elif title == "Average Length of Stay":
                display_value = f"{kpi_value:.2f} days"

            else:
                display_value = f"{kpi_value:.2f} minutes"

        # ----------------------------------------------
        # READMISSION RATE
        # ----------------------------------------------

        elif spec["type"] == "readmission":

            total_readmitted = df[
                "readmitted_discharges"
            ].sum()

            total_eligible = df[
                "eligible_discharges"
            ].sum()

            if total_eligible == 0:
                st.warning(
                    "Readmission rate cannot be calculated. "
                    "A complete 30-day follow-up window is required."
                )
                continue

            kpi_value = (
                total_readmitted / total_eligible
            ) * 100

            trend = df.groupby(
                date_col, as_index=False
            ).agg(
                readmitted=("readmitted_discharges", "sum"),
                eligible=("eligible_discharges", "sum")
            )

            trend[metric] = (
                trend["readmitted"] /
                trend["eligible"].replace(0, float("nan"))
            ) * 100

            trend = trend.dropna(subset=[metric])

            display_value = f"{kpi_value:.2f}%"

        # ----------------------------------------------
        # PHYSICIAN PRODUCTIVITY
        # ----------------------------------------------

        else:

            kpi_value = df[metric].sum()

            trend = df.groupby(
                date_col, as_index=False
            )[metric].sum()

            display_value = f"{kpi_value:,.0f}"

        # ----------------------------------------------
        # DISPLAY KPI
        # ----------------------------------------------

        st.metric(
            label=f"Selected Period – {spec['unit']}",
            value=display_value
        )

        # ----------------------------------------------
        # PLOTLY CHART
        # ----------------------------------------------

        trend = trend.sort_values(date_col)

        fig = px.line(
            trend,
            x=date_col,
            y=metric,
            markers=True,
            title=f"{title} – {chart_label}"
        )

        fig.update_layout(
            template="plotly_white",
            xaxis_title=dict(
            text=xaxis_label,
            font=dict(color = "#102638",size=13)
            ),
            yaxis_title=dict(
            text=spec["unit"],
            font=dict(color="#102638",size=13)
            ),
            height=350,
            hovermode="x unified",
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            font=dict(
                family="Arial",
                color="#102638",
                size=12
            ),
            title=dict(
                font=dict(
                    size=17,
                    color="#102638"
                )
            ),
            margin=dict(
                l=55,
                r=25,
                t=60,
                b=55
            ),
            xaxis=dict(
                showgrid=False,
                linecolor="#CBD5DC",
                tickfont=dict(
                color="#294354",
                size=11
                ),
                title_font=dict(
                color="#102638",
                size=13
                ),
                tickformat="%b %Y"
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor="#E8EEF2",
                zeroline=False,
                tickfont=dict(
                color="#294354",
                size=11
                ),
                title_font=dict(
                color="#102638",
                size=13
                )
            ),
            legend=dict(
            font=dict(color="#294354")
            )
        )

        fig.update_traces(
            line=dict(
                color="#16A994",
                width=3
            ),
            marker=dict(
                color="#16A994",
                size=7,
                line=dict(
                    color="#FFFFFF",
                    width=1
                )
            ),
            hovertemplate="%{x}<br>%{y:,.2f}<extra></extra>"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


except Exception as e:

    st.error(
        "Could not load dashboard data. "
        "Check MySQL connection and aggregate tables."
    )

    st.exception(e)

