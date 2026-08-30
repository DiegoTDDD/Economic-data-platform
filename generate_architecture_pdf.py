from fpdf import FPDF
from datetime import datetime

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.set_text_color(0, 51, 102)
        self.cell(0, 10, 'Economic Intelligence & Financial Markets Platform', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, 'Official Architecture & Data Engineering Documentation', 0, 1, 'C')
        self.line(10, 30, 200, 30)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()} | Generated on {datetime.now().strftime("%m/%d/%Y %H:%M")}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_text_color(0, 51, 102)
        self.ln(10)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(2)

    def chapter_body(self, body):
        self.set_font('Arial', '', 11)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 7, body)
        self.ln(2)

pdf = PDF()
pdf.add_page()

pdf.chapter_title('1. Project Overview')
overview_text = (
    "The Economic Intelligence Platform is an end-to-end enterprise Data Engineering solution. "
    "Its objective is to extract, process, and store macroeconomic indicators from the Central Bank "
    "of Brazil (SGS) and historical cryptocurrency data (Yahoo Finance), consolidating everything into "
    "a Data Warehouse (PostgreSQL) for consumption via an Interactive Dashboard (Streamlit)."
)
pdf.chapter_body(overview_text)

pdf.chapter_title('2. Architecture & Infrastructure')
architecture_text = (
    "The infrastructure is 100% containerized using Docker and Docker Compose, ensuring isolation "
    "and reproducibility. The orchestrated services include:\n\n"
    "- economics_postgres_gold: Relational Database (PostgreSQL 15).\n"
    "- economics_pipeline: Python extraction orchestrator (Pandas, Requests, yFinance).\n"
    "- economics_dashboard: Analytical web application (Streamlit + Plotly).\n\n"
    "Quality control is handled via CI/CD on GitHub Actions, which spins up the database and runs "
    "unit tests on every new commit to the main branch."
)
pdf.chapter_body(architecture_text)

pdf.chapter_title('3. Ingestion Models (Extract & Load)')
ingestion_text = (
    "The pipelines operate with error handling, dynamic typing, and resilient connections:\n"
    "1. Cryptocurrency (BTC-USD): Daily ingestion of closing price and trading volume.\n"
    "2. Macroeconomics: Collection of IPCA (Monthly), Unemployment Rate (Series 24369), and the "
    "USD/BRL exchange rate.\n\n"
    "Data is sanitized (drop_duplicates, dropna) before being loaded via SQLAlchemy."
)
pdf.chapter_body(ingestion_text)

pdf.chapter_title('4. Data Modeling (Gold Layer)')
modeling_text = (
    "The Economics Gold database contains the following optimized tables:\n\n"
    "- gold_bitcoin_metrics: date (PK), close_price, volume.\n"
    "- gold_economic_indicators: date (PK), indicator_name (PK), value.\n\n"
    "The tables use direct relational schemas to facilitate performant analytical queries."
)
pdf.chapter_body(modeling_text)

pdf.output('Architecture_Documentation.pdf')
print("[+] PDF report successfully generated: Architecture_Documentation.pdf")
