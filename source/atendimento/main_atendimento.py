"""
HyperAutomation — Orquestrador do Processo 1 (Setor de Atendimento).

Fluxo completo:
    1. Receber Solicitação  — leitura de e-mails via IMAP
    2. Baixar Documentos    — anexos salvos em ERP_Portal_Fake/Downloads/
    3. Validar Documentação — verifica documentos obrigatórios
    4. Classificar Arquivos — move para Documentos_OK/ ou Documentos_Pendentes/
    5. Responder ao Cliente — e-mail automático via SMTP
    6. Encaminhar           — move solicitações completas para Encaminhados/

Execução:
    python source/atendimento/main_atendimento.py
"""

import logging
import sys
from pathlib import Path

from dotenv import load_dotenv

# Permite execução direta e importação como módulo
_RAIZ_PROJETO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_RAIZ_PROJETO / "source"))
sys.path.insert(0, str(_RAIZ_PROJETO / "source" / "atendimento"))

from atendimento.classificacao import classificar_solicitacao, encaminhar_solicitacao  # noqa: E402
from atendimento.leitura_email import receber_solicitacoes  # noqa: E402
from atendimento.resposta_cliente import responder_cliente  # noqa: E402
from atendimento.validacao import validar_documentacao  # noqa: E402

# ── Configuração de Logging ────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            _RAIZ_PROJETO / "evidencias" / "atendimento.log",
            encoding="utf-8",
        ),
    ],
)

logger = logging.getLogger("main_atendimento")

_PASTA_ERP = _RAIZ_PROJETO / "ERP_Portal_Fake"


def _banner(texto: str, largura: int = 60) -> None:
    print("=" * largura)
    print(f"  {texto}")
    print("=" * largura)


def processar_solicitacao(solicitacao: dict, enviar_email_resposta: bool = True) -> dict:
    """
    Executa as etapas 3–6 para uma única solicitação.

    Args:
        solicitacao: Dicionário retornado por receber_solicitacoes().
        enviar_email_resposta: Se False, pula o envio de e-mail (modo simulação).

    Returns:
        Dicionário com o resultado do processamento:
            - id_solicitacao, remetente, completa, pasta_final, status
    """
    id_sol = solicitacao["id_solicitacao"]
    remetente = solicitacao["remetente"]
    assunto = solicitacao["assunto"]
    pasta_downloads = solicitacao["pasta_downloads"]
    anexos = solicitacao["anexos"]

    logger.info("─" * 50)
    logger.info("Processando solicitação: %s", id_sol)
    logger.info("Remetente: %s | Assunto: %s", remetente, assunto)
    logger.info("Anexos recebidos (%d): %s", len(anexos), anexos)

    # ── Etapa 3: Validar Documentação ─────────────────────────────────────────
    logger.info("[3/6] Validando documentação...")
    resultado = validar_documentacao(pasta_downloads, anexos)

    # ── Etapa 4: Classificar Arquivos ─────────────────────────────────────────
    logger.info("[4/6] Classificando arquivos...")
    pasta_classificada = classificar_solicitacao(
        pasta_downloads,
        _PASTA_ERP,
        resultado["completa"],
    )

    # ── Etapa 5: Responder ao Cliente ─────────────────────────────────────────
    logger.info("[5/6] Respondendo ao cliente...")
    if enviar_email_resposta:
        try:
            responder_cliente(remetente, assunto, resultado)
        except Exception as erro:
            logger.error("Falha ao enviar resposta ao cliente: %s", erro)
    else:
        status_str = "COMPLETA" if resultado["completa"] else "PENDENTE"
        logger.info(
            "  [SIMULAÇÃO] E-mail de resposta não enviado. "
            "Situação: %s",
            status_str,
        )

    # ── Etapa 6: Encaminhar ───────────────────────────────────────────────────
    pasta_final = pasta_classificada
    if resultado["completa"]:
        logger.info("[6/6] Encaminhando ao próximo setor...")
        pasta_final = encaminhar_solicitacao(pasta_classificada, _PASTA_ERP)
    else:
        logger.info(
            "[6/6] Encaminhamento IGNORADO — documentação incompleta. "
            "Aguardando reenvio do cliente."
        )

    status = "encaminhada" if resultado["completa"] else "pendente"

    return {
        "id_solicitacao": id_sol,
        "remetente": remetente,
        "completa": resultado["completa"],
        "pasta_final": pasta_final,
        "status": status,
    }


def main(enviar_email_resposta: bool = True) -> None:
    """Executa o fluxo completo do Processo 1 — Atendimento."""
    load_dotenv()

    _banner("HyperAutomation — Processo 1: Setor de Atendimento")

    # Garantir estrutura ERP
    for subpasta in ("Downloads", "Documentos_OK", "Documentos_Pendentes", "Encaminhados"):
        (_PASTA_ERP / subpasta).mkdir(parents=True, exist_ok=True)

    # Garantir pasta de evidências
    (_RAIZ_PROJETO / "evidencias").mkdir(exist_ok=True)

    # ── Etapa 1 + 2: Receber e Baixar ─────────────────────────────────────────
    print("\n[1-2/6] Recebendo solicitações e baixando documentos...")
    logger.info("Iniciando leitura de e-mails via IMAP...")

    try:
        solicitacoes = receber_solicitacoes(_PASTA_ERP)
    except Exception as erro:
        logger.error("Falha crítica ao receber solicitações: %s", erro)
        sys.exit(1)

    if not solicitacoes:
        logger.info("Nenhuma nova solicitação encontrada. Processo finalizado.")
        print("\nNenhuma nova solicitação encontrada.")
        return

    logger.info("Total de solicitações recebidas: %d", len(solicitacoes))

    # ── Etapas 3–6: Processar cada solicitação ────────────────────────────────
    resultados = []
    erros = 0

    for i, solicitacao in enumerate(solicitacoes, start=1):
        print(f"\n[Solicitação {i}/{len(solicitacoes)}]")
        try:
            resultado = processar_solicitacao(solicitacao, enviar_email_resposta)
            resultados.append(resultado)
        except Exception as erro:
            logger.error(
                "Erro inesperado ao processar '%s': %s",
                solicitacao["id_solicitacao"],
                erro,
            )
            erros += 1

    # ── Resumo ────────────────────────────────────────────────────────────────
    completas = sum(1 for r in resultados if r["completa"])
    pendentes = len(resultados) - completas

    _banner("Resumo do Processo 1")
    print(f"  Total de solicitações:  {len(solicitacoes)}")
    print(f"  Processadas com sucesso: {len(resultados)}")
    print(f"  Documentação completa:  {completas}")
    print(f"  Documentação pendente:  {pendentes}")
    print(f"  Erros:                  {erros}")
    print("=" * 60)

    for r in resultados:
        icone = "✓" if r["completa"] else "✗"
        print(f"  {icone} {r['remetente']} → {r['status']}")

    print(f"\n  Log salvo em: evidencias/atendimento.log")
    print("=" * 60)


if __name__ == "__main__":
    main()
