from fpdf import FPDF
from datetime import datetime

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.set_text_color(0, 51, 102)
        self.cell(0, 10, 'Economic Intelligence & Financial Markets Platform', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, 'Documentacao Oficial de Arquitetura e Engenharia de Dados', 0, 1, 'C')
        self.line(10, 30, 200, 30)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Página {self.page_no()} | Gerado em {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 0, 'C')

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

# Instancia o PDF
pdf = PDF()
pdf.add_page()

# Seção 1: Visão Geral
pdf.chapter_title('1. Visao Geral do Projeto')
texto_visao = (
    "A Economic Intelligence Platform e uma solucao corporativa end-to-end de Engenharia de Dados. "
    "Seu objetivo e extrair, tratar e armazenar indicadores macroeconomicos do Banco Central do Brasil (SGS) "
    "e dados historicos de criptomoedas (Yahoo Finance), consolidando tudo em um Data Warehouse (PostgreSQL) "
    "para consumo via Dashboard Interativo (Streamlit)."
)
pdf.chapter_body(texto_visao)

# Seção 2: Arquitetura e Infraestrutura
pdf.chapter_title('2. Arquitetura e Infraestrutura')
texto_arq = (
    "A infraestrutura foi 100% containerizada utilizando Docker e Docker Compose, garantindo isolamento "
    "e reprodutibilidade. Os servicos orquestrados incluem:\n\n"
    "- economics_postgres_gold: Banco de Dados Relacional (PostgreSQL 15).\n"
    "- economics_pipeline: Orquestrador de extracao em Python (Pandas, Requests, yFinance).\n"
    "- economics_dashboard: Aplicacao web analitica (Streamlit + Plotly).\n\n"
    "O controle de qualidade e feito via CI/CD no GitHub Actions, que levanta a base e roda testes unitarios "
    "a cada novo commit na branch principal."
)
pdf.chapter_body(texto_arq)

# Seção 3: Pipelines de Ingestao
pdf.chapter_title('3. Modelos de Ingestao (Extract & Load)')
texto_ing = (
    "Os pipelines operam com tratamento de erros, tipagem dinamica e conexao resiliente:\n"
    "1. Criptomoedas (BTC-USD): Ingestao diaria de preco de fechamento e volume de negociacao.\n"
    "2. Macroeconomia: Coleta de IPCA (Mensal), Taxa de Desemprego (Serie 24369) e Cambio Dolar-Real (USD/BRL).\n\n"
    "Os dados sao higienizados (drop_duplicates, dropna) antes do carregamento via SQLAlchemy."
)
pdf.chapter_body(texto_ing)

# Seção 4: Modelagem de Dados (Gold Layer)
pdf.chapter_title('4. Modelagem de Dados (Gold Layer)')
texto_mod = (
    "O banco de dados Economics Gold contem as seguintes tabelas otimizadas:\n\n"
    "- gold_bitcoin_metrics: date (PK), close_price, volume.\n"
    "- gold_economic_indicators: date (PK), indicator_name (PK), value.\n\n"
    "As tabelas possuem schemas relacionais diretos para facilitar consultas analiticas performaticas."
)
pdf.chapter_body(texto_mod)

# Gera o arquivo
pdf.output('Documentacao_Arquitetura.pdf')
print("[+] Relatorio PDF gerado com sucesso: Documentacao_Arquitetura.pdf")
