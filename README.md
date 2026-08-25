# 📊 Economic Intelligence & Financial Markets Platform

![Python](https://img.shields.io/badge/Python-3.10-blue?style=for-the-badge&logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?style=for-the-badge&logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Containerized-blue?style=for-the-badge&logo=docker)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red?style=for-the-badge&logo=streamlit)

Uma plataforma end-to-end de Engenharia de Dados desenvolvida para extrair, transformar e visualizar indicadores macroeconômicos (Banco Central do Brasil) e dados históricos de criptomoedas (Yahoo Finance).

---

## 🏗️ Arquitetura do Projeto

O projeto foi construído seguindo as melhores práticas de Data Engineering, estruturado 100% em containers Docker para garantir isolamento e reprodutibilidade.

1. **Extract & Load (EL):** Scripts em Python (`pandas`, `requests`, `yfinance`) que extraem dados via API e carregam em um Data Warehouse.
2. **Storage (Gold Layer):** Banco de dados relacional (PostgreSQL) otimizado para consultas analíticas.
3. **Analytics & Visualization:** Dashboard interativo construído com Streamlit e Plotly.
4. **CI/CD:** Pipeline automatizado no GitHub Actions para testes e validação contínua.

📄 **[Clique aqui para baixar a Documentação Oficial de Arquitetura em PDF](Documentacao_Arquitetura.pdf)**

---

## 📸 Demonstração Visual

### 1. Visualização Analítica (Camada de Consumo)
**Indicadores Macroeconômicos Empilhados (IPCA, Taxa de Desemprego e Câmbio):**
![Macroeconomic Dashboard](assets/macro.png)

**Histórico de Criptomoedas (Bitcoin - Preço e Volume):**
![Bitcoin Dashboard](assets/bitcoin.png)

### 2. Motor de Engenharia (Processo de ETL/ELT)
**Orquestração e Execução do Pipeline (Logs do Docker):**
![Pipeline Logs](assets/logs.png)

**Armazenamento na Camada Gold (PostgreSQL):**
![Database Preview](assets/database.png)

**Automação e Testes (CI/CD no GitHub Actions):**
![GitHub Actions CI/CD](assets/actions.png)

---

## 🚀 Como Executar o Projeto Localmente

**Pré-requisitos:** Ter o `Docker` e o `Docker Compose` instalados.

1. Clone o repositório:
```bash
git clone [https://github.com/DiegoTDDD/Economic-data-platform.git](https://github.com/DiegoTDDD/Economic-data-platform.git)
cd Economic-data-platform