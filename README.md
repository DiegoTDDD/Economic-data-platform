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