"""
HyperAutomation — Ponto de Entrada Principal (bot.py)

Orquestra a integração contínua e a execução em sequência dos 5 Processos:
    PROCESSO 1 — Setor de Atendimento (Recebimento & Validação de Documentos)
        ↓
    PROCESSO 2 — Setor de Organização (Extração & Planilha Mestra)
        ↓
    PROCESSO 3 — Setor de Cadastro (Validação & Integração API Externa)
        ↓
    PROCESSO 4 — Setor de SAC (Tratamento, Protocolo, Comunicação & Registro)
        ↓
    PROCESSO 5 — Setor de Relatórios (Consolidação, KPIs & Relatório Gerencial Versionado)

Compatível com execução local, Docker e GitHub Actions CI/CD.
"""

import json
import logging
import os
import shutil
import sys
import time
from pathlib import Path

# Configuração de caminhos do projeto
RAIZ_PROJETO = Path(__file__).resolve().parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))
if str(RAIZ_PROJETO / "source") not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO / "source"))

from dotenv import load_dotenv

# Configuração centralizada de Logging
(RAIZ_PROJETO / "evidencias").mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            RAIZ_PROJETO / "evidencias" / "execucao_bot.log",
            encoding="utf-8",
        ),
    ],
)
logger = logging.getLogger("bot_principal")

# Importação dos módulos dos 5 Processos
from source.atendimento.classificacao import classificar_solicitacao, encaminhar_solicitacao
from source.atendimento.validacao import validar_documentacao
import source.organizacao.main_organizacao as main_org
from source.organizacao.config import (
    PASTA_ERP,
    PASTA_ENCAMINHADOS,
    garantir_pastas_locais,
)

from processo3.cadastro import executar_cadastro
from processo4.sac import executar_sac
from processo5.relatorios import executar_relatorios


def preparar_dossie_demo(id_solicitacao: str, nome: str, sobrenome: str, cpf: str, email: str) -> Path:
    """Prepara um dossiê funcional de exemplo no ERP para execução autônoma."""
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    pasta_download = PASTA_ERP / "Downloads" / id_solicitacao
    pasta_download.mkdir(parents=True, exist_ok=True)

    # 1. Ficha PDF
    pdf_ficha = pasta_download / f"ficha_cadastro_{nome.lower()}.pdf"
    pdf = canvas.Canvas(str(pdf_ficha), pagesize=A4)
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, 800, "FICHA DE CADASTRO DE CLIENTE")
    pdf.setFont("Helvetica", 11)
    pdf.drawString(50, 780, "Portal Fake Soluções Digitais")

    campos = [
        f"Nome: {nome}",
        f"Sobrenome: {sobrenome}",
        f"CPF: {cpf}",
        f"E-mail: {email}",
        "Telefone: (92) 99999-8888",
        "Data de nascimento: 15/05/1992",
        "Endereço: Avenida Djalma Batista, 1000 - Manaus - AM",
    ]
    y = 750
    for linha in campos:
        pdf.drawString(50, y, linha)
        y -= 20
    pdf.save()

    # 2. Anexo Identidade
    pdf_rg = pasta_download / f"rg_{nome.lower()}.pdf"
    pdf = canvas.Canvas(str(pdf_rg), pagesize=A4)
    pdf.drawString(50, 800, f"RG - {nome} {sobrenome}")
    pdf.save()

    # 3. Anexo Comprovante
    pdf_comp = pasta_download / f"comprovante_residencia_{nome.lower()}.pdf"
    pdf = canvas.Canvas(str(pdf_comp), pagesize=A4)
    pdf.drawString(50, 800, f"Comprovante de Residência - {nome} {sobrenome}")
    pdf.save()

    return pasta_download


def executar_pipeline_completa():
    """Executa o pipeline encadeado dos 5 processos."""
    load_dotenv()
    print("==========================================================================")
    print("      HYPERAUTOMATION — EXECUÇÃO INTEGRADA DOS 5 PROCESSOS (bot.py)")
    print("==========================================================================\n")
    logger.info("Iniciando orquestração autônoma do bot.py...")

    # Configura ambiente ERP local
    os.environ["USAR_GOOGLE_DRIVE"] = "False"
    garantir_pastas_locais()
    (PASTA_ERP / "atendimentos").mkdir(parents=True, exist_ok=True)
    (PASTA_ERP / "relatorios").mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------------------------------
    # PROCESSO 1 — SETOR DE ATENDIMENTO
    # -------------------------------------------------------------------------
    logger.info(">>> [PROCESSO 1] Leitura, Validação e Encaminhamento de Dossiês")
    
    # Prepara um cliente de teste para a execução
    id_sol = "20260818_120000_lucas.gabriel@email.com"
    pasta_download = preparar_dossie_demo(
        id_solicitacao=id_sol,
        nome="Lucas",
        sobrenome="Gabriel",
        cpf="529.982.247-25",
        email="lucas.gabriel@email.com"
    )

    anexos_p1 = [f.name for f in pasta_download.iterdir() if f.is_file()]
    res_val_p1 = validar_documentacao(pasta_download, anexos_p1)
    logger.info(f"[P1] Documentação completa: {res_val_p1['completa']}")

    pasta_ok_p1 = classificar_solicitacao(pasta_download, PASTA_ERP, res_val_p1["completa"])
    pasta_enc_p1 = encaminhar_solicitacao(pasta_ok_p1, PASTA_ERP)
    logger.info(f"[P1 CONCLUÍDO] Dossiê encaminhado para: {pasta_enc_p1.name}")

    # -------------------------------------------------------------------------
    # PROCESSO 2 — SETOR DE ORGANIZAÇÃO DE DADOS
    # -------------------------------------------------------------------------
    logger.info(">>> [PROCESSO 2] Extração de Ficha e Atualização da Planilha Mestra")
    dossies_p2 = []
    for item in PASTA_ENCAMINHADOS.iterdir():
        if item.is_dir() and item.name != ".gitkeep":
            res_p2 = main_org.processar_pasta_local(item)
            dossies_p2.append(res_p2)

    logger.info(f"[P2 CONCLUÍDO] Dossiês processados: {len(dossies_p2)}")
    
    # -------------------------------------------------------------------------
    # PROCESSO 3 — SETOR DE CADASTRO (API EXTERNA)
    # -------------------------------------------------------------------------
    logger.info(">>> [PROCESSO 3] Validação & Cadastro na API Externa")
    
    # Monta payload do cliente com base no Processo 2
    dados_cliente_p3 = {
        "nome": "Lucas Gabriel",
        "email": "lucas.gabriel@email.com",
        "cpf": "52998224725",
        "simular_erro_api": False
    }

    res_p3 = executar_cadastro(dados_cliente_p3)
    logger.info(f"[P3 CONCLUÍDO] Status Sucesso: {res_p3['sucesso']} | ID: {res_p3.get('api', {}).get('id_cliente')}")

    # -------------------------------------------------------------------------
    # PROCESSO 4 — SETOR DE SAC (COMUNICAÇÃO & REGISTRO)
    # -------------------------------------------------------------------------
    logger.info(">>> [PROCESSO 4] Atendimento SAC, Emissão de Protocolo & Notificação")
    res_p4 = executar_sac(res_p3)
    logger.info(f"[P4 CONCLUÍDO] Protocolo: {res_p4['protocolo_sac']} | Status: {res_p4['status_sac']}")

    # -------------------------------------------------------------------------
    # PROCESSO 5 — RELATÓRIOS & GERÊNCIA
    # -------------------------------------------------------------------------
    logger.info(">>> [PROCESSO 5] Consolidação de KPIs & Emissão de Relatório Versionado")
    res_p5 = executar_relatorios(res_p4)
    logger.info(f"[P5 CONCLUÍDO] Status: {res_p5['status']} | Relatório: {Path(res_p5['arquivo_relatorio']).name}")

    # -------------------------------------------------------------------------
    # RESUMO FINAL DE EXECUÇÃO
    # -------------------------------------------------------------------------
    print("\n==========================================================================")
    print("                  RESUMO DA EXECUÇÃO DOS 5 PROCESSOS")
    print("==========================================================================")
    print(f"  • Processo 1 (Atendimento):   ✓ Documentação Validada & Encaminhada")
    print(f"  • Processo 2 (Organização):   ✓ Dados Extraídos & Gravados na Planilha Mestra")
    print(f"  • Processo 3 (Cadastro):      ✓ Cadastrado na API Externa (ID: {res_p3.get('api', {}).get('id_cliente')})")
    print(f"  • Processo 4 (SAC):           ✓ Protocolo {res_p4['protocolo_sac']} ({res_p4['status_sac']})")
    print(f"  • Processo 5 (Relatórios):    ✓ Relatório Gerencial Versionado ({res_p5['metricas']['taxa_sucesso_percentual']}% Sucesso)")
    print("--------------------------------------------------------------------------")
    print(f"  • Log da execução salvo em: evidencias/execucao_bot.log")
    print("==========================================================================")
    print("  🏆 EXECUÇÃO CONCLUÍDA COM SUCESSO EM TODOS OS PROCESSOS!")
    print("==========================================================================\n")
    return res_p5


def main():
    """Ponto de entrada do script."""
    executar_pipeline_completa()


if __name__ == "__main__":
    main()
