import os
import pandas as pd
import streamlit as st
import plotly.express as px
from sqlalchemy import create_engine

st.set_page_config(page_title="Economic & Crypto Intelligence Platform", layout="wide")

st.title("📊 Economic Intelligence & Financial Markets Platform")
st.markdown("Production-grade analytical dashboard powered by PostgreSQL, Python, and Streamlit.")

@st.cache_resource
def get_engine():
    db_host = os.getenv("DB_HOST", "localhost")
    return create_engine(f"postgresql://admin:adminpassword@{db_host}:5432/economics_gold")

engine = get_engine()

# Load Data
try:
    df_btc = pd.read_sql("SELECT * FROM gold_bitcoin_metrics ORDER BY date ASC", engine)
    df_macro = pd.read_sql("SELECT * FROM gold_economic_indicators ORDER BY date ASC", engine)
except Exception as e:
    st.error(f"Database connection error: {e}")
    st.stop()

# Sidebar filters
st.sidebar.header("Filter Options")
selected_indicators = st.sidebar.multiselect(
    "Select Macroeconomic Indicators",
    options=df_macro['indicator_name'].unique() if not df_macro.empty else [],
    default=df_macro['indicator_name'].unique() if not df_macro.empty else []
)

# Main Layout - Tabs
tab1, tab2 = st.tabs(["🚀 Cryptocurrency Analytics (Bitcoin)", "📈 Macroeconomic Indicators"])

with tab1:
    st.subheader("Bitcoin Historical Close Price & Volume")
    if not df_btc.empty:
        fig_btc = px.line(df_btc, x='date', y='close_price', title="BTC-USD Daily Close Price")
        st.plotly_chart(fig_btc, use_container_width=True)
        
        fig_vol = px.bar(df_btc, x='date', y='volume', title="BTC-USD Trading Volume")
        st.plotly_chart(fig_vol, use_container_width=True)
    else:
        st.info("No Bitcoin metrics found in database. Run pipeline orchestrator.")

with tab2:
    st.subheader("Macroeconomic Intelligence (BCB SGS)")
    if not df_macro.empty and selected_indicators:
        filtered_macro = df_macro[df_macro['indicator_name'].isin(selected_indicators)]
        fig_macro = px.line(
            filtered_macro, 
            x='date', 
            y='value', 
            color='indicator_name', 
            title="Macroeconomic Indicators Time Series"
        )
        st.plotly_chart(fig_macro, use_container_width=True, key="macro_chart_unique_key")
    else:
        st.info("Select indicators from the sidebar or run data ingestion.")
