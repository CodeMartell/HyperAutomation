import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("Processo5_Relatorios")


PASTA_RELATORIOS = (
    Path(__file__).resolve().parent.parent
    / "ERP_Portal_Fake"
    / "relatorios"
)

ARQUIVO_HISTORICO = PASTA_RELATORIOS / "historico_relatorios.json"


def inicializar_estrutura() -> None:
    """
    Cria a pasta e o arquivo utilizados pelo Processo 5.
    """

    PASTA_RELATORIOS.mkdir(parents=True, exist_ok=True)

    if not ARQUIVO_HISTORICO.exists():
        with open(ARQUIVO_HISTORICO, "w", encoding="utf-8") as arquivo:
            json.dump([], arquivo, ensure_ascii=False, indent=4)

    logger.info("Estrutura de relatórios inicializada.")


def validar_dados_processo4(resultado_p4: Dict[str, Any]) -> bool:
    """
    Verifica se os dados recebidos do Processo 4 podem ser processados.
    """

    logger.info("Validando dados recebidos do Processo 4.")

    if not isinstance(resultado_p4, dict):
        logger.error("Dados do Processo 4 estão em formato inválido.")
        return False

    if not resultado_p4.get("dados_prontos_para_p5", False):
        logger.warning(
            "Processo 4 não marcou os dados como prontos para o Processo 5."
        )

    return True


def carregar_historico() -> List[Dict[str, Any]]:
    """
    Carrega os relatórios gerados anteriormente.
    """

    inicializar_estrutura()

    try:
        with open(ARQUIVO_HISTORICO, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)

            if isinstance(dados, list):
                return dados

    except Exception as erro:
        logger.error(f"Erro ao carregar histórico: {erro}")

    return []


def gerar_metricas(
    resultado_p4: Dict[str, Any],
    historico: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Consolida os dados e gera métricas gerenciais.
    """

    logger.info("Gerando métricas e indicadores.")

    status_atual = resultado_p4.get("status_sac", "DESCONHECIDO")

    registros = historico.copy()

    # Inclui a execução atual na contagem.
    status_anteriores = [
        item.get("status_sac", "DESCONHECIDO")
        for item in registros
    ]

    todos_status = status_anteriores + [status_atual]

    total = len(todos_status)

    concluidos = sum(
        1 for status in todos_status
        if status == "CONCLUIDO"
    )

    duplicidades = sum(
        1 for status in todos_status
        if status == "ALERTA_DUPLICIDADE"
    )

    pendencias = sum(
        1 for status in todos_status
        if status == "PENDENCIA_TECNICA"
    )

    comunicacoes_retidas = sum(
        1 for status in todos_status
        if status == "COMUNICACAO_RETIDA"
    )

    fallbacks = sum(
        1 for status in todos_status
        if status == "FALLBACK"
    )

    taxa_sucesso = (
        round((concluidos / total) * 100, 2)
        if total > 0
        else 0
    )

    return {
        "total_atendimentos": total,
        "cadastros_concluidos": concluidos,
        "duplicidades": duplicidades,
        "pendencias_tecnicas": pendencias,
        "comunicacoes_retidas": comunicacoes_retidas,
        "fallbacks": fallbacks,
        "taxa_sucesso_percentual": taxa_sucesso
    }


def gerar_relatorio(
    resultado_p4: Dict[str, Any],
    metricas: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Gera o relatório gerencial da execução.
    """

    logger.info("Gerando relatório gerencial.")

    cliente = resultado_p4.get("cliente", {})
    monitoramento_p4 = resultado_p4.get("monitoramento", {})

    versao = datetime.now().strftime("%Y%m%d_%H%M%S")

    relatorio = {
        "versao": versao,
        "data_geracao": datetime.now().isoformat(),
        "processo": "Processo 5 - Relatórios e Gerência",

        "protocolo_sac": resultado_p4.get("protocolo_sac"),
        "status_sac": resultado_p4.get("status_sac"),

        "cliente": {
            "nome": cliente.get("nome"),
            "email": cliente.get("email"),
            "cpf": cliente.get("cpf")
        },

        "monitoramento_processo4": monitoramento_p4,

        "metricas": metricas,

        "status_processo5": "CONCLUIDO"
    }

    return relatorio


def salvar_relatorio(relatorio: Dict[str, Any]) -> Path:
    """
    Salva o relatório individual e também atualiza o histórico.
    """

    logger.info("Salvando e versionando relatório.")

    inicializar_estrutura()

    versao = relatorio["versao"]

    arquivo_relatorio = (
        PASTA_RELATORIOS
        / f"relatorio_gerencial_{versao}.json"
    )

    with open(
        arquivo_relatorio,
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(
            relatorio,
            arquivo,
            ensure_ascii=False,
            indent=4
        )

    historico = carregar_historico()
    historico.append(relatorio)

    with open(
        ARQUIVO_HISTORICO,
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(
            historico,
            arquivo,
            ensure_ascii=False,
            indent=4
        )

    logger.info(
        f"Relatório salvo com sucesso: {arquivo_relatorio.name}"
    )

    return arquivo_relatorio


def fallback_relatorio(erro: str) -> Dict[str, Any]:
    """
    Fallback do Processo 5.
    """

    logger.error(
        f"Fallback do Processo 5 acionado: {erro}"
    )

    return {
        "sucesso": False,
        "processo": "Processo 5",
        "status": "FALLBACK",
        "erro": erro,
        "timestamp": datetime.now().isoformat()
    }


def executar_relatorios(
    resultado_p4: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Função principal do Processo 5.

    Fluxo:
        Processo 4
        ↓
        Consolidação
        ↓
        Métricas
        ↓
        Relatório Gerencial
        ↓
        Processo concluído
    """

    logger.info("======================================")
    logger.info(" INICIANDO PROCESSO 5 - RELATÓRIOS")
    logger.info("======================================")

    try:

        # 1. Validar entrada
        if not validar_dados_processo4(resultado_p4):
            raise ValueError(
                "Dados recebidos do Processo 4 são inválidos."
            )

        # 2. Carregar resultados anteriores
        historico = carregar_historico()

        # 3. Consolidar e gerar métricas
        metricas = gerar_metricas(
            resultado_p4,
            historico
        )

        # 4. Gerar relatório gerencial
        relatorio = gerar_relatorio(
            resultado_p4,
            metricas
        )

        # 5. Versionar e salvar
        caminho = salvar_relatorio(relatorio)

        logger.info(
            "Processo 5 concluído com sucesso."
        )

        return {
            "sucesso": True,
            "status": "PROCESSO_CONCLUIDO",
            "relatorio": relatorio,
            "arquivo_relatorio": str(caminho),
            "metricas": metricas
        }

    except Exception as erro:

        logger.exception(
            "Erro durante execução do Processo 5."
        )

        return fallback_relatorio(str(erro))