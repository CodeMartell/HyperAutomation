"""
Módulo de configurações para o Processo 2 (Organização de Dados).
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Caminho raiz do projeto
RAIZ_PROJETO = Path(__file__).resolve().parent.parent.parent

# Estrutura ERP local
PASTA_ERP = RAIZ_PROJETO / "ERP_Portal_Fake"
PASTA_DOWNLOADS = PASTA_ERP / "Downloads"
PASTA_OK = PASTA_ERP / "Documentos_OK"
PASTA_PENDENTES = PASTA_ERP / "Documentos_Pendentes"
PASTA_ENCAMINHADOS = PASTA_ERP / "Encaminhados"

# Pastas exclusivas do Processo 2
PASTA_SISTEMA_INTEGRADOR = PASTA_ERP / "Sistema_Integrador_Portal_Fake"
CAMINHO_PLANILHA = PASTA_SISTEMA_INTEGRADOR / "Planilha_Mestra.xlsx"
PASTA_ARQUIVADOS = PASTA_ERP / "Arquivados"

# Configurações do Google Drive
USAR_DRIVE = os.getenv("USAR_GOOGLE_DRIVE", "False").lower() in ("true", "1", "yes")

# Garantir criação local de diretórios básicos para o processo
def garantir_pastas_locais():
    """Garante que a estrutura de diretórios locais necessários exista."""
    for pasta in (PASTA_OK, PASTA_PENDENTES, PASTA_ENCAMINHADOS, PASTA_SISTEMA_INTEGRADOR, PASTA_ARQUIVADOS):
        pasta.mkdir(parents=True, exist_ok=True)
