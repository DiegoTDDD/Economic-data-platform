import os
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sqlalchemy import create_engine

# Configuração da página
st.set_page_config(page_title="Economic Intelligence", layout="wide")

# Conexão com o Banco de Dados (com cache para performance)
@st.cache_data
def load_data():
    db_host = os.getenv("DB_HOST", "localhost")
    engine = create_engine(f"postgresql://admin:adminpassword@{db_host}:5432/economics_gold")
    
    df_btc = pd.read_sql("SELECT * FROM gold_bitcoin_metrics ORDER BY date", engine)
    df_macro = pd.read_sql("SELECT * FROM gold_economic_indicators ORDER BY date", engine)
    
    return df_btc, df_macro

df_btc, df_macro = load_data()

# Cabeçalho
st.title("📊 Economic Intelligence & Financial Markets Platform")
st.markdown("Production-grade analytical dashboard powered by PostgreSQL, Python, and Streamlit.")

# Menu Lateral (Filtros)
st.sidebar.header("Filter Options")
indicators = df_macro['indicator_name'].unique().tolist()
selected_indicators = st.sidebar.multiselect("Select Macroeconomic Indicators", indicators, default=indicators)

# Abas do Dashboard
tab1, tab2 = st.tabs(["🚀 Cryptocurrency Analytics (Bitcoin)", "📈 Macroeconomic Indicators"])

# Aba 1: Bitcoin
with tab1:
    st.subheader("Bitcoin Historical Close Price & Volume")
    
    fig_btc_price = px.line(df_btc, x='date', y='close_price', title="BTC-USD Daily Close Price")
    st.plotly_chart(fig_btc_price, use_container_width=True)
    
    fig_btc_vol = px.area(df_btc, x='date', y='volume', title="BTC-USD Trading Volume")
    st.plotly_chart(fig_btc_vol, use_container_width=True)

# Aba 2: Macroeconomia (Atualizada com Subplots independentes)
with tab2:
    st.subheader("Macroeconomic Intelligence (BCB SGS)")
    
    if not selected_indicators:
        st.warning("Please select at least one indicator from the sidebar.")
    else:
        # Cria subplots empilhados dinamicamente com base na quantidade de filtros selecionados
        fig_macro = make_subplots(
            rows=len(selected_indicators), 
            cols=1, 
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=selected_indicators
        )
        
        # Paleta de cores padrão do Plotly
        colors = px.colors.qualitative.Plotly
        
        # Adiciona cada linha no seu próprio eixo Y (gráfico independente)
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
        
        # Ajusta a altura de forma dinâmica: 250 pixels por gráfico selecionado
        fig_macro.update_layout(
            height=280 * len(selected_indicators), 
            showlegend=False,
            title_text="Macroeconomic Indicators Time Series",
            margin=dict(t=50, b=40, l=40, r=40)
        )
        
        st.plotly_chart(fig_macro, use_container_width=True)
