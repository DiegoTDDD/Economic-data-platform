import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

# Page configuration
st.set_page_config(page_title="Economic Intelligence", layout="wide")

# Committed export of the Gold tables (export_snapshot.py), used when no database is configured,
# as on Streamlit Community Cloud.
SNAPSHOT_DIR = Path(__file__).resolve().parents[1] / "data" / "gold_snapshot"


@st.cache_data
def load_data():
    """Gold tables from PostgreSQL when DB_PASSWORD is set, else the committed snapshot."""
    if os.getenv("DB_PASSWORD"):
        import sys

        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from analytics_models.gold import engine_from_env

        engine = engine_from_env()
        df_btc = pd.read_sql("SELECT * FROM gold_bitcoin_metrics ORDER BY date", engine)
        df_macro = pd.read_sql("SELECT * FROM gold_economic_indicators ORDER BY date", engine)
        return df_btc, df_macro, "live PostgreSQL Gold layer"
    df_btc = pd.read_parquet(SNAPSHOT_DIR / "gold_bitcoin_metrics.parquet")
    df_macro = pd.read_parquet(SNAPSHOT_DIR / "gold_economic_indicators.parquet")
    return df_btc, df_macro, "snapshot of the Gold layer"


df_btc, df_macro, data_source = load_data()

# Header
st.title("📊 Economic Intelligence & Financial Markets Platform")
st.markdown("Production-grade analytical dashboard powered by PostgreSQL, Python, and Streamlit.")
latest = max(pd.to_datetime(df_btc["date"]).max(), pd.to_datetime(df_macro["date"]).max())
st.caption(f"Data: {data_source}, latest observation {latest:%Y-%m-%d}.")

# Sidebar menu (Filters)
st.sidebar.header("Filter Options")
indicators = df_macro['indicator_name'].unique().tolist()
selected_indicators = st.sidebar.multiselect("Select Macroeconomic Indicators", indicators, default=indicators)

# Dashboard tabs
tab1, tab2 = st.tabs(["🚀 Cryptocurrency Analytics (Bitcoin)", "📈 Macroeconomic Indicators"])

# Tab 1: Bitcoin
with tab1:
    st.subheader("Bitcoin Historical Close Price & Volume")

    fig_btc_price = px.line(df_btc, x='date', y='close_price', title="BTC-USD Daily Close Price")
    st.plotly_chart(fig_btc_price, width="stretch")

    fig_btc_vol = px.area(df_btc, x='date', y='volume', title="BTC-USD Trading Volume")
    st.plotly_chart(fig_btc_vol, width="stretch")

# Tab 2: Macroeconomics (updated with independent subplots)
with tab2:
    st.subheader("Macroeconomic Intelligence (BCB SGS)")

    if not selected_indicators:
        st.warning("Please select at least one indicator from the sidebar.")
    else:
        # Dynamically build stacked subplots based on the number of selected filters
        fig_macro = make_subplots(
            rows=len(selected_indicators),
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=selected_indicators
        )

        # Default Plotly color palette
        colors = px.colors.qualitative.Plotly

        # Add each line on its own Y axis (independent chart)
        for i, indicator in enumerate(selected_indicators):
            df_ind = df_macro[df_macro['indicator_name'] == indicator]
            fig_macro.add_trace(
                go.Scatter(
                    x=df_ind['date'],
                    y=df_ind['value'],
                    name=indicator,
                    mode='lines',
                    line=dict(color=colors[i % len(colors)])
                ),
                row=i+1, col=1
            )

        # Dynamically adjust height: 280 pixels per selected chart
        fig_macro.update_layout(
            height=280 * len(selected_indicators),
            showlegend=False,
            title_text="Macroeconomic Indicators Time Series",
            margin=dict(t=50, b=40, l=40, r=40)
        )

        st.plotly_chart(fig_macro, width="stretch")
