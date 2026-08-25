# 📊 Economic Intelligence & Financial Markets Data Platform

Production-grade, highly scalable data engineering architecture designed to ingest, process, store, and visualize real-time macroeconomic indicators and cryptocurrency market metrics.

---

## 🏗️ System Architecture
# 1. Recria o README.md sem caracteres de formatação que quebram o bash
cat << 'EOF' > README.md
# Economic Intelligence and Financial Markets Data Platform

Production-grade, highly scalable data engineering architecture designed to ingest, process, store, and visualize real-time macroeconomic indicators and cryptocurrency market metrics.

## System Architecture

[ Central Bank API (BCB SGS) ] ---> [ Python Ingestion Pipelines ] ---> [ PostgreSQL Gold Layer ] ---> [ Streamlit Dashboard ]
[ Yahoo Finance (BTC & USD) ] --->         (Pandas & Requests)             (Dockerized)                 (Plotly Visualizations)

## Core Components

* Data Ingestion (analytics_models/): Automated extraction of Brazilian macroeconomic series (IPCA, Unemployment Rate) and financial assets (Bitcoin, USD/BRL exchange rates) using robust API sessions and rate-limiting safeguards.
* Storage Layer (database_init.py): Relational schema optimized for analytical queries running on containerized PostgreSQL.
* Orchestrator (orchestrator.py): Master workflow runner executing initialization, extraction, and validation sequentially with comprehensive logging.
* Analytical Dashboard (dashboards/main_dashboard.py): Interactive web application powered by Streamlit and Plotly for deep exploratory data analysis.
* CI/CD (.github/workflows/ci_pipeline.yml): Automated continuous integration pipeline testing database contracts and ingestion reliability on every commit.

## Quick Start Guide

1. Spin up Infrastructure:
   make up

2. Run End-to-End Pipeline:
   make pipeline

3. Launch Dashboard:
   make dashboard

4. Execute Unit Tests:
   make test
