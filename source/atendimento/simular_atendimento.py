"""
Script de simulação end-to-end — Processo 1 (Atendimento).

Demonstra o fluxo completo SEM necessidade de conta de e-mail real:
    1. Cria arquivos de teste simulando anexos enviados pelo cliente
    2. Executa validação, classificação e resposta (sem envio de e-mail)
    3. Exibe o estado final da estrutura ERP_Portal_Fake/

Cenários simulados:
    A) Solicitação COMPLETA — todos os 3 documentos presentes
    B) Solicitação PENDENTE — apenas 1 documento enviado

Uso:
    python source/atendimento/simular_atendimento.py
"""

import logging
import shutil
import sys
from pathlib import Path

# Permite execução direta
_RAIZ_PROJETO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_RAIZ_PROJETO / "source"))
sys.path.insert(0, str(_RAIZ_PROJETO / "source" / "atendimento"))

from source.atendimento.classificacao import (  # noqa: E402
    classificar_solicitacao,
    encaminhar_solicitacao,
)
from source.atendimento.validacao import validar_documentacao  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("simulacao")

_PASTA_ERP = _RAIZ_PROJETO / "ERP_Portal_Fake"


def _criar_estrutura_erp() -> None:
    """Garante que a estrutura ERP_Portal_Fake existe."""
    for subpasta in ("Downloads", "Documentos_OK", "Documentos_Pendentes", "Encaminhados"):
        (_PASTA_ERP / subpasta).mkdir(parents=True, exist_ok=True)
    logger.info("Estrutura ERP_Portal_Fake verificada/criada.")


def _criar_arquivos_teste(pasta: Path, nomes: list[str]) -> None:
    """Cria arquivos de texto vazios simulando anexos PDF/imagem."""
    pasta.mkdir(parents=True, exist_ok=True)
    for nome in nomes:
        (pasta / nome).write_text(
            f"[SIMULAÇÃO] Arquivo de teste: {nome}\n"
            "Este arquivo simula um documento real enviado pelo cliente.",
            encoding="utf-8",
        )
    logger.info("Arquivos de teste criados em: %s", pasta)


def _exibir_arvore_erp() -> None:
    """Exibe a estrutura atual do ERP_Portal_Fake."""
    print("\n📁 Estado final do ERP_Portal_Fake/")
    print("─" * 45)

    for subpasta in ("Downloads", "Documentos_OK", "Documentos_Pendentes", "Encaminhados"):
        pasta = _PASTA_ERP / subpasta
        arquivos = list(pasta.rglob("*")) if pasta.exists() else []
        arquivos = [f for f in arquivos if f.is_file() and f.name != ".gitkeep"]

        print(f"  ├── {subpasta}/  ({len(arquivos)} arquivo(s))")
        for arq in arquivos:
            caminho_relativo = arq.relative_to(_PASTA_ERP / subpasta)
            print(f"  │   └── {caminho_relativo}")

    print("─" * 45)


def simular_cenario(
    nome_cenario: str,
    id_solicitacao: str,
    remetente: str,
    assunto: str,
    anexos: list[str],
) -> dict:
    """
    Executa um cenário de simulação completo.

    Args:
        nome_cenario: Descrição do cenário para exibição.
        id_solicitacao: Identificador único da solicitação.
        remetente: E-mail fictício do cliente.
        assunto: Assunto fictício do e-mail.
        anexos: Lista de nomes de arquivos simulados.

    Returns:
        Resultado do processamento (mesmo formato de processar_solicitacao).
    """
    print(f"\n{'=' * 55}")
    print(f"  Cenário: {nome_cenario}")
    print(f"  Remetente: {remetente}")
    print(f"  Assunto: {assunto}")
    print(f"  Anexos: {', '.join(anexos)}")
    print("=" * 55)

    # Criar arquivos de teste na pasta Downloads
    pasta_downloads = _PASTA_ERP / "Downloads" / id_solicitacao
    _criar_arquivos_teste(pasta_downloads, anexos)

    # Etapa 3: Validação
    logger.info("[3/6] Validando documentação...")
    resultado = validar_documentacao(pasta_downloads, anexos)

    # Etapa 4: Classificação
    logger.info("[4/6] Classificando arquivos...")
    pasta_classificada = classificar_solicitacao(
        pasta_downloads,
        _PASTA_ERP,
        resultado["completa"],
    )

    # Etapa 5: Resposta (simulada)
    status_str = "COMPLETA ✓" if resultado["completa"] else "PENDENTE ✗"
    logger.info("[5/6] [SIMULAÇÃO] Resposta ao cliente: situação %s", status_str)
    print(f"\n  📧 [SIMULAÇÃO] E-mail de resposta ao cliente ({remetente}):")
    print(f"     Assunto: Re: {assunto}")
    print(f"     Situação: {status_str}")

    if not resultado["completa"]:
        pendentes_label = [p.replace("_", " ").title() for p in resultado["pendentes"]]
        print(f"     Documentos faltantes: {', '.join(pendentes_label)}")

    # Etapa 6: Encaminhar (se completo)
    pasta_final = pasta_classificada
    if resultado["completa"]:
        logger.info("[6/6] Encaminhando ao próximo setor...")
        pasta_final = encaminhar_solicitacao(pasta_classificada, _PASTA_ERP)
        print(f"\n  ✓ Solicitação encaminhada ao próximo setor.")
    else:
        logger.info("[6/6] Encaminhamento ignorado — aguardando documentação.")
        print(f"\n  ✗ Solicitação retida em Documentos_Pendentes/.")

    return {
        "id_solicitacao": id_solicitacao,
        "remetente": remetente,
        "completa": resultado["completa"],
        "pasta_final": pasta_final,
        "status": "encaminhada" if resultado["completa"] else "pendente",
    }


def main() -> None:
    """Executa a simulação completa com dois cenários."""
    print("=" * 55)
    print("  HyperAutomation — Simulação do Processo 1")
    print("  Setor de Atendimento — Portal Fake Soluções Digitais")
    print("=" * 55)
    print("\n⚠  Modo SIMULAÇÃO — nenhum e-mail real será enviado.")

    _criar_estrutura_erp()

    resultados = []

    # ── Cenário A: Documentação COMPLETA ─────────────────────────────────────
    resultado_a = simular_cenario(
        nome_cenario="Documentação COMPLETA",
        id_solicitacao="20260728_100000_joao.silva@exemplo.com",
        remetente="joao.silva@exemplo.com",
        assunto="Solicitação de Atendimento — João Silva",
        anexos=[
            "rg_joao_silva.pdf",
            "comprovante_residencia_jan2026.pdf",
            "ficha_cadastro_preenchida.pdf",
        ],
    )
    resultados.append(resultado_a)

    # ── Cenário B: Documentação INCOMPLETA ───────────────────────────────────
    resultado_b = simular_cenario(
        nome_cenario="Documentação INCOMPLETA (falta ficha e comprovante)",
        id_solicitacao="20260728_100001_maria.souza@exemplo.com",
        remetente="maria.souza@exemplo.com",
        assunto="Documentos para Atendimento — Maria Souza",
        anexos=[
            "cnh_frente_verso.pdf",
        ],
    )
    resultados.append(resultado_b)

    # ── Resumo ────────────────────────────────────────────────────────────────
    print(f"\n{'=' * 55}")
    print("  RESUMO DA SIMULAÇÃO")
    print("=" * 55)
    for r in resultados:
        icone = "✓" if r["completa"] else "✗"
        print(f"  {icone} {r['remetente']} → {r['status'].upper()}")
        print(f"     Pasta final: {r['pasta_final'].relative_to(_RAIZ_PROJETO)}")

    _exibir_arvore_erp()

    print("\n  ✓ Simulação concluída com sucesso!")
    print("  Para executar com e-mails reais, configure o .env e execute:")
    print("  $ python source/atendimento/main_atendimento.py")
    print("=" * 55)


if __name__ == "__main__":
    main()
