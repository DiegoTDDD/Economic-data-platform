# Economic Intelligence & Financial Markets Platform

![CI/CD Pipeline Status](https://github.com/DiegoTDDD/Economic-data-platform/actions/workflows/ci_pipeline.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Gold_Layer-336791?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?logo=streamlit&logoColor=white)

An end-to-end ELT (Extract, Load, Transform) data platform that ingests macroeconomic indicators and cryptocurrency market data, structures it into a strict PostgreSQL "Gold" layer, and serves it through interactive operational dashboards.

📄 **[Read the Full Engineering Case Study (PDF)](./manuscript/Economic_Platform_Case_Study.pdf)**

---

## 🏛️ Project Architecture & Pipeline Flow

The platform is built as a modular, containerized ELT pipeline. It separates extraction, transactional storage, orchestration, and presentation into isolated layers to guarantee reproducibility and data integrity.

```text
[ Disparate APIs ] ---> [ Python Ingestion ] ---> [ PostgreSQL Gold Layer ] ---> [ Streamlit Dashboards ]
                              |                              |
                        (Modular Scripts)             (Strict Relational Schema)
```

## 🚀 Demonstration & Visual Evidence

1. **Ingestion & Orchestration Logs**
   Modular extraction scripts fetch, validate, and normalize raw JSON payloads into clean DataFrames before inserting them into the database.
2. **PostgreSQL Gold Layer Schema**
   Enforcing schema-on-write with ACID guarantees, ensuring analytical queries run on clean, normalized time-series data.
3. **Macroeconomic & Financial Dashboards**
   Interactive Streamlit dashboards powered by optimized SQL queries directly from the Gold layer.
4. **CI/CD Automation (GitHub Actions)**
   Automated build-and-test pipeline validating code quality on every push.

## 🛠️ Tech Stack & Components

| Layer | Component | Purpose |
|---|---|---|
| Ingestion | Python (requests, pandas) | API data extraction, JSON parsing, and type enforcement. |
| Storage | PostgreSQL | ACID-compliant relational storage for clean time-series metrics. |
| Orchestration | Python (orchestrator.py) | Execution sequencing and safe database dependency initialization. |
| Infrastructure | Docker & Docker Compose | Network isolation and environment-agnostic reproducibility. |
| CI/CD | GitHub Actions | Automated build and test pipeline on every repository push. |
| Presentation | Streamlit & Plotly | Interactive operations console and real-time visualization. |

## ⚙️ Run Locally

**Prerequisites**
* Docker Desktop
* Git

**1. Clone the repository**
```bash
git clone https://github.com/DiegoTDDD/Economic-data-platform.git
cd Economic-data-platform
```

**2. Start the environment**
```bash
cd infrastructure
docker compose up -d --build
```

**3. Check the containers**
```bash
docker compose ps
```

**4. Open the dashboard**
Open your browser and navigate to `http://localhost:8501`.

**5. Stop the environment**
```bash
docker compose down
```

## 📊 Data Sources

* **IBGE:** IPCA inflation index and Unemployment metrics.
* **Banco Central do Brasil (BCB SGS):** Official exchange rates.
* **yfinance API:** Historical Bitcoin (BTC-USD) market prices.

*Note: Raw data is dynamically extracted via APIs; no static datasets are hardcoded in the repository.*