"""
Script de simulação end-to-end — Processo 2 (Organização de Dados).

Demonstra o fluxo completo do orquestrador localmente:
    1. Inicializa o cenário com dados de teste estruturados (válidos e inválidos).
    2. Executa a primeira varredura, extraindo, validando, escrevendo e arquivando.
    3. Cria um cenário de reprocessamento (duplicado) para demonstrar a idempotência.
    4. Executa a segunda varredura, arquivando o duplicado diretamente.
    5. Exibe a planilha de controle preenchida e a árvore de diretórios resultante.
"""

import os
# Força modo local na simulação para evitar problemas de quota/Drive
os.environ["USAR_GOOGLE_DRIVE"] = "False"

import logging
import sys
import shutil
from pathlib import Path

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# Permite execução direta
_RAIZ_PROJETO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_RAIZ_PROJETO / "source"))
sys.path.insert(0, str(_RAIZ_PROJETO / "source" / "organizacao"))

from organizacao.config import PASTA_ERP, PASTA_OK, PASTA_ARQUIVADOS, CAMINHO_PLANILHA, garantir_pastas_locais
import organizacao.main_organizacao as main_org

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger("simulacao_organizacao")

def _limpar_ambiente_teste() -> None:
    """Limpa e reseta pastas e planilhas antigas da simulação."""
    for subpasta in ("Downloads", "Documentos_OK", "Documentos_Pendentes", "Encaminhados", "Arquivados", "Sistema_Integrador_Portal_Fake"):
        pasta = PASTA_ERP / subpasta
        if pasta.exists():
            shutil.rmtree(pasta)
    garantir_pastas_locais()
    logger.info("Estrutura do ERP limpa e resetada para a simulação.")

def _criar_documento_ficha(pasta: Path, nome_arquivo: str, conteudo: str) -> None:
    """
    Cria um PDF verdadeiro contendo o conteúdo da ficha.
    """
    pasta.mkdir(parents=True, exist_ok=True)

    caminho_pdf = pasta / nome_arquivo

    pdf = canvas.Canvas(str(caminho_pdf), pagesize=A4)

    largura, altura = A4
    y = altura - 50

    pdf.setFont("Helvetica", 12)

    for linha in conteudo.splitlines():
        pdf.drawString(50, y, linha)
        y -= 20

        if y < 50:
            pdf.showPage()
            pdf.setFont("Helvetica", 12)
            y = altura - 50

    pdf.save()
    
def _criar_pdf_simples(pasta: Path, nome_arquivo: str, titulo: str) -> None:
    """
    Cria um PDF simples para simular documentos anexos.
    """
    caminho_pdf = pasta / nome_arquivo

    pdf = canvas.Canvas(str(caminho_pdf), pagesize=A4)

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, 800, titulo)

    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, 770, "Documento utilizado apenas para simulação.")

    pdf.save()
    
    

def _exibir_arvore_erp() -> None:
    """Exibe de forma visual a árvore de diretórios do ERP."""
    print("\n📁 Estado final da estrutura ERP_Portal_Fake/")
    print("─" * 60)

    for subpasta in ("Downloads", "Documentos_OK", "Documentos_Pendentes", "Encaminhados", "Arquivados", "Sistema_Integrador_Portal_Fake"):
        pasta = PASTA_ERP / subpasta
        arquivos = list(pasta.rglob("*")) if pasta.exists() else []
        arquivos = [f for f in arquivos if f.is_file() and f.name != ".gitkeep"]

        print(f"  ├── {subpasta}/  ({len(arquivos)} arquivo(s))")
        for arq in arquivos:
            caminho_relativo = arq.relative_to(PASTA_ERP / subpasta)
            print(f"  │   └── {caminho_relativo}")

    print("─" * 60)

def main() -> None:
    print("=" * 60)
    print("  HyperAutomation — Simulação do Processo 2")
    print("  Setor de Organização de Dados — Portal Fake")
    print("=" * 60)

    _limpar_ambiente_teste()

    # ── Cenário 1: Criar dossiê VÁLIDO (João Silva) ──────────────────────────
    logger.info("Criando dossiê de teste VÁLIDO (João Silva)...")
    joao_dir = PASTA_OK / "20260728_100000_joao.silva@exemplo.com"
    joao_ficha = (
        "FICHA DE CADASTRO DE CLIENTE\n"
        "Portal Fake Soluções Digitais\n"
        "Nome: João\n"
        "Sobrenome: Silva\n"
        "CPF: 529.982.247-25\n"
        "E-mail: joao.silva@exemplo.com\n"
        "Telefone: (92) 99999-9999\n"
        "Data de nascimento: 01/01/2000\n"
        "Endereço: Rua das Flores, 123 - Manaus - AM"
    )
    _criar_documento_ficha(joao_dir, "ficha_cadastro_preenchida.pdf", joao_ficha)
    _criar_pdf_simples(joao_dir, "rg_joao_silva.pdf", "RG - João Silva")
    _criar_pdf_simples(joao_dir, "comprovante_residencia.pdf", "Comprovante de Residência")

    # ── Cenário 2: Criar dossiê INVÁLIDO (Maria Souza) ──────────────────────
    logger.info("Criando dossiê de teste INVÁLIDO (Maria Souza)...")
    maria_dir = PASTA_OK / "20260728_100001_maria.souza@exemplo.com"
    maria_ficha = (
        "FICHA DE CADASTRO DE CLIENTE\n"
        "Portal Fake Soluções Digitais\n"
        "Nome: Maria\n"
        "Sobrenome: Souza\n"
        "CPF: 999.999.999-99\n"  # CPF com números repetidos (inválido)
        "E-mail: maria.souza.invalido\n"  # E-mail sem formato @
        "Telefone: (92) 98888-88\n"  # Telefone incompleto
        "Data de nascimento: 31/02/1995\n"  # Data inexistente
        "Endereço: Rua"  # Endereço muito curto
    )
    _criar_documento_ficha(maria_dir, "ficha_cadastro.pdf", maria_ficha)    
    _criar_pdf_simples(maria_dir, "cnh.pdf", "CNH - Maria Souza")

    print("\n>>> INICIANDO EXECUÇÃO 1/2 (Processando Fichas Iniciais) <<<")
    main_org.main()

    # ── Cenário 3: Reprocessar João Silva (Duplicado) ────────────────────────
    print("\n>>> PREPARANDO EXECUÇÃO 2/2 (Teste de Idempotência) <<<")
    logger.info("Recriando dossiê idêntico de João Silva na pasta OK...")
    
    _criar_documento_ficha(joao_dir, "ficha_cadastro_preenchida.pdf", joao_ficha)

    _criar_pdf_simples(
    joao_dir,
    "rg_joao_silva.pdf",
    "RG - João Silva"
)

    _criar_pdf_simples(
    joao_dir,
    "comprovante_residencia.pdf",
    "Comprovante de Residência"
)

    print("\n>>> INICIANDO EXECUÇÃO 2/2 (Processando Dossiê Duplicado) <<<")
    main_org.main()

    _exibir_arvore_erp()

    print("\n Planilha Mestra gerada com sucesso!")
    print(f" Caminho: {CAMINHO_PLANILHA.relative_to(_RAIZ_PROJETO)}")
    print("=" * 60)
    print("  Simulação do Processo 2 concluída com sucesso!")
    print("=" * 60)

if __name__ == "__main__":
    main()
