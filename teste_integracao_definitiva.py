"""
HyperAutomation — Teste Integrado Definitivo (End-to-End Master Pipeline)

Este script executa a integração completa entre TODOS os processos do ecossistema:
    Processo 1 (Atendimento & Validação de Documentos)
        ↓
    Processo 2 (Organização de Dados, Extração & Planilha Mestra)
        ↓
    Processo 3 (Validação & Cadastro via API Externa)
        ↓
    Processo 4 (SAC — Tratamento, Protocolo, Comunicação & Registro)
        ↓
    Processo 5 (Relatórios Gerenciais, Indicadores e Métricas Globais)

Executa a validação de fluxos de sucesso e tratamento de exceções (duplicidade, falha técnica, fallback).
"""

import json
import logging
import os
import shutil
import sys
import time
from pathlib import Path

# Configuração de ambiente e caminhos
os.environ["USAR_GOOGLE_DRIVE"] = "False"
RAIZ_PROJETO = Path(__file__).resolve().parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))
if str(RAIZ_PROJETO / "source") not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO / "source"))

# Importação dos módulos de cada processo
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# Processo 1
from source.atendimento.classificacao import classificar_solicitacao, encaminhar_solicitacao
from source.atendimento.validacao import validar_documentacao

# Processo 2
import source.organizacao.main_organizacao as main_org
from source.organizacao.config import (
    PASTA_ARQUIVADOS,
    PASTA_ENCAMINHADOS,
    PASTA_ERP,
    PASTA_OK,
    garantir_pastas_locais,
)

# Processo 3
from processo3.cadastro import executar_cadastro

# Processo 4
from processo4.sac import executar_sac

# Processo 5
from processo5.relatorios import executar_relatorios

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("teste_integracao_definitiva")


def resetar_ambiente_erp() -> None:
    """Prepara uma estrutura limpa do ERP para a simulação master."""
    logger.info("Resetando ambiente de testes em ERP_Portal_Fake/...")
    for subpasta in ("Downloads", "Documentos_OK", "Documentos_Pendentes", "Encaminhados", "Arquivados", "Sistema_Integrador_Portal_Fake", "atendimentos", "relatorios"):
        pasta = PASTA_ERP / subpasta
        if pasta.exists():
            shutil.rmtree(pasta)
    garantir_pastas_locais()
    (PASTA_ERP / "atendimentos").mkdir(parents=True, exist_ok=True)
    (PASTA_ERP / "relatorios").mkdir(parents=True, exist_ok=True)
    logger.info("Estrutura ERP resetada com sucesso.")


def criar_ficha_pdf(caminho_pdf: Path, nome: str, sobrenome: str, cpf: str, email: str) -> None:
    """Cria um PDF real com formato reconhecível pelo extrator do Processo 2."""
    caminho_pdf.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(caminho_pdf), pagesize=A4)
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, 800, "FICHA DE CADASTRO DE CLIENTE")
    pdf.setFont("Helvetica", 11)
    pdf.drawString(50, 780, "Portal Fake Soluções Digitais")
    
    conteudo = [
        f"Nome: {nome}",
        f"Sobrenome: {sobrenome}",
        f"CPF: {cpf}",
        f"E-mail: {email}",
        "Telefone: (92) 99999-8888",
        "Data de nascimento: 15/05/1992",
        "Endereço: Avenida Djalma Batista, 1000 - Manaus - AM",
    ]
    
    y = 750
    for linha in conteudo:
        pdf.drawString(50, y, linha)
        y -= 20
    pdf.save()


def criar_pdf_anexo(caminho_pdf: Path, titulo: str) -> None:
    """Cria anexo genérico PDF para checklist do Processo 1."""
    caminho_pdf.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(caminho_pdf), pagesize=A4)
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, 800, titulo)
    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, 780, "Documento simulado para validação.")
    pdf.save()


def executar_teste_definitivo():
    print("==========================================================================")
    print("      HYPERAUTOMATION — TESTE INTEGRADO DEFINITIVO (PROC 1 A 5)")
    print("==========================================================================\n")

    resetar_ambiente_erp()

    # =========================================================================
    # FLUXO 1: EXECUÇÃO COMPLETA DE UM CLIENTE VÁLIDO (Lucas Gabriel)
    # =========================================================================
    print(">>> [FLUXO MASTER 1] Processando Cliente Válido (Lucas Gabriel)")
    
    id_solicitacao = "20260817_100000_lucas.gabriel@email.com"
    pasta_download = PASTA_ERP / "Downloads" / id_solicitacao

    # 1.1 Criar anexos para Processo 1
    criar_ficha_pdf(
        pasta_download / "ficha_cadastro_lucas.pdf",
        nome="Lucas",
        sobrenome="Gabriel",
        cpf="529.982.247-25",
        email="lucas.gabriel@email.com"
    )
    criar_pdf_anexo(pasta_download / "rg_lucas_gabriel.pdf", "RG - Lucas Gabriel")
    criar_pdf_anexo(pasta_download / "comprovante_residencia_lucas.pdf", "Comprovante de Residência")

    # --- EXECUÇÃO PROCESSO 1 ---
    logger.info("[P1] Validando documentação de Lucas Gabriel...")
    anexos_p1 = [f.name for f in pasta_download.iterdir() if f.is_file()]
    res_val_p1 = validar_documentacao(pasta_download, anexos_p1)
    assert res_val_p1["completa"] is True, "Documentação de Lucas Gabriel deveria estar COMPLETA"
    logger.info("[P1] Documentação completa! Classificando e encaminhando...")

    pasta_ok_p1 = classificar_solicitacao(pasta_download, PASTA_ERP, res_val_p1["completa"])
    pasta_enc_p1 = encaminhar_solicitacao(pasta_ok_p1, PASTA_ERP)
    logger.info(f"[P1 CONCLUÍDO] Dossiê encaminhado para: {pasta_enc_p1.relative_to(RAIZ_PROJETO)}")

    # --- EXECUÇÃO PROCESSO 2 ---
    logger.info("[P2] Extraindo dados da ficha e gerando Planilha Mestra...")
    res_p2_lista = []
    for item in PASTA_ENCAMINHADOS.iterdir():
        if item.is_dir() and item.name != ".gitkeep":
            res_p2 = main_org.processar_pasta_local(item)
            res_p2_lista.append(res_p2)

    assert len(res_p2_lista) == 1
    res_p2_lucas = res_p2_lista[0]
    assert res_p2_lucas["status"] == "VALIDADO"
    logger.info(f"[P2 CONCLUÍDO] Dados validados para: {res_p2_lucas['nome_cliente']} (Hash: {res_p2_lucas['hash'][:8]})")

    # --- EXECUÇÃO PROCESSO 3 ---
    dados_cliente_p3 = {
        "nome": "Lucas Gabriel",
        "email": "lucas.gabriel@email.com",
        "cpf": "52998224725",
        "simular_erro_api": False
    }
    logger.info("[P3] Solicitando cadastro via API externa...")
    res_p3 = executar_cadastro(dados_cliente_p3)
    assert res_p3["sucesso"] is True
    logger.info(f"[P3 CONCLUÍDO] Cliente cadastrado com ID: {res_p3['api']['id_cliente']}")

    # --- EXECUÇÃO PROCESSO 4 (SAC) ---
    logger.info("[P4] Executando atendimento SAC, gerando protocolo e enviando comunicação...")
    res_p4 = executar_sac(res_p3)
    assert res_p4["sucesso"] is True
    assert res_p4["status_sac"] == "CONCLUIDO"
    logger.info(f"[P4 CONCLUÍDO] Protocolo SAC: {res_p4['protocolo_sac']} | Tempo: {res_p4['monitoramento']['tempo_execucao_ms']} ms")

    # --- EXECUÇÃO PROCESSO 5 (RELATÓRIOS) ---
    logger.info("[P5] Consolidando métricas e gerando relatório gerencial...")
    res_p5 = executar_relatorios(res_p4)
    assert res_p5["sucesso"] is True
    assert res_p5["status"] == "PROCESSO_CONCLUIDO"
    logger.info(f"[P5 CONCLUÍDO] Relatório gerado em: {Path(res_p5['arquivo_relatorio']).name}")
    print("✔ FLUXO MASTER 1 COMPLETO COM SUCESSO!\n" + "-" * 74 + "\n")

    # =========================================================================
    # FLUXO 2: TENTATIVA DE DUPLICIDADE (Lucas Gabriel reprocessado)
    # =========================================================================
    print(">>> [FLUXO MASTER 2] Testando Duplicidade de Cadastro (Lucas Gabriel)")
    res_p3_dup = executar_cadastro(dados_cliente_p3)
    assert res_p3_dup["sucesso"] is False
    assert "já cadastrado" in res_p3_dup["mensagem"]

    res_p4_dup = executar_sac(res_p3_dup)
    assert res_p4_dup["status_sac"] == "ALERTA_DUPLICIDADE"

    res_p5_dup = executar_relatorios(res_p4_dup)
    assert res_p5_dup["sucesso"] is True
    assert res_p5_dup["metricas"]["duplicidades"] >= 1
    logger.info(f"[P5 INDICADORES] Métricas atualizadas — Total: {res_p5_dup['metricas']['total_atendimentos']}, Duplicidades: {res_p5_dup['metricas']['duplicidades']}")
    print("✔ FLUXO MASTER 2 (DUPLICIDADE) VERIFICADO COM SUCESSO!\n" + "-" * 74 + "\n")

    # =========================================================================
    # FLUXO 3: TRATAMENTO DE FALHA TÉCNICA E RECOVERY
    # =========================================================================
    print(">>> [FLUXO MASTER 3] Testando Falha Técnica na API e Tratamento SAC")
    cliente_erro_api = {
        "nome": "Mariana Costa",
        "email": "mariana.costa@email.com",
        "cpf": "98765432111",
        "simular_erro_api": True
    }
    res_p3_erro = executar_cadastro(cliente_erro_api)
    assert res_p3_erro["sucesso"] is False

    res_p4_erro = executar_sac(res_p3_erro)
    assert res_p4_erro["status_sac"] == "PENDENCIA_TECNICA"

    res_p5_erro = executar_relatorios(res_p4_erro)
    assert res_p5_erro["sucesso"] is True
    assert res_p5_erro["metricas"]["pendencias_tecnicas"] >= 1
    logger.info(f"[P5 INDICADORES] Métricas atualizadas — Pendências Técnicas: {res_p5_erro['metricas']['pendencias_tecnicas']}")
    print("✔ FLUXO MASTER 3 (PENDÊNCIA TÉCNICA) VERIFICADO COM SUCESSO!\n" + "-" * 74 + "\n")

    # =========================================================================
    # EXIBIÇÃO DO PAINEL FINAL DE RESULTADOS
    # =========================================================================
    print("==========================================================================")
    print("                  PAINEL FINAL DE VERIFICAÇÃO DO ERP")
    print("==========================================================================")
    
    metricas_finais = res_p5_erro["metricas"]
    print(f"  • Total de Atendimentos Processados:  {metricas_finais['total_atendimentos']}")
    print(f"  • Cadastros Concluídos com Sucesso:  {metricas_finais['cadastros_concluidos']}")
    print(f"  • Solicitacoes Duplicadas Tratas:     {metricas_finais['duplicidades']}")
    print(f"  • Pendências Técnicas Notificadas:  {metricas_finais['pendencias_tecnicas']}")
    print(f"  • Taxa de Sucesso Operacional:       {metricas_finais['taxa_sucesso_percentual']}%")
    print("--------------------------------------------------------------------------")
    print(f"  • Histórico SAC Gravado: ERP_Portal_Fake/atendimentos/registro_atendimentos_sac.json")
    print(f"  • Relatórios Versionados: ERP_Portal_Fake/relatorios/")
    print("==========================================================================")
    print("  🏆 INTEGRALIZAÇÃO DEFINITIVA COMPROVADA — TODOS OS PROC. FUNCIONANDO OK!")
    print("==========================================================================\n")


if __name__ == "__main__":
    executar_teste_definitivo()
