"""
Módulo de classificação de arquivos — Processo 1 (Atendimento).

Responsável por mover a pasta de uma solicitação para o diretório
correto dentro do ERP_Portal_Fake, conforme o resultado da validação:

    - Documentação COMPLETA  → ERP_Portal_Fake/Documentos_OK/<id>/
    - Documentação INCOMPLETA → ERP_Portal_Fake/Documentos_Pendentes/<id>/
    - Após resposta ao cliente → ERP_Portal_Fake/Encaminhados/<id>/
      (somente para solicitações completas)

Justificativa:
    shutil.move — stdlib do Python, sem dependências extras.
    Operação atômica suficiente para o ambiente simulado (sistema de arquivos local).
    Em produção com Google Drive, seria substituída por chamadas à Drive API.
"""

import logging
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)


def classificar_solicitacao(
    pasta_solicitacao: Path,
    pasta_erp: Path,
    completa: bool,
) -> Path:
    """
    Move a pasta da solicitação para Documentos_OK ou Documentos_Pendentes.

    Args:
        pasta_solicitacao: Pasta atual da solicitação (em Downloads/).
        pasta_erp: Raiz do ERP_Portal_Fake.
        completa: True se a documentação está completa.

    Returns:
        Novo caminho da pasta da solicitação após a movimentação.

    Raises:
        FileNotFoundError: Se a pasta da solicitação não existir.
        shutil.Error: Em caso de falha na movimentação.
    """
    if not pasta_solicitacao.exists():
        raise FileNotFoundError(
            f"Pasta da solicitação não encontrada: {pasta_solicitacao}"
        )

    if completa:
        destino_base = pasta_erp / "Documentos_OK"
        status_label = "OK"
    else:
        destino_base = pasta_erp / "Documentos_Pendentes"
        status_label = "PENDENTE"

    destino_base.mkdir(parents=True, exist_ok=True)
    destino = destino_base / pasta_solicitacao.name

    # Se já existir (execução duplicada), adiciona sufixo
    if destino.exists():
        destino = destino_base / f"{pasta_solicitacao.name}_dup"

    shutil.move(str(pasta_solicitacao), str(destino))

    logger.info(
        "Solicitação '%s' classificada como %s → %s",
        pasta_solicitacao.name,
        status_label,
        destino,
    )

    return destino


def encaminhar_solicitacao(
    pasta_solicitacao: Path,
    pasta_erp: Path,
) -> Path:
    """
    Move uma solicitação completa de Documentos_OK para Encaminhados/.

    Representa o encaminhamento ao próximo setor após a resposta ao cliente.

    Args:
        pasta_solicitacao: Caminho atual da solicitação (em Documentos_OK/).
        pasta_erp: Raiz do ERP_Portal_Fake.

    Returns:
        Novo caminho da pasta após o encaminhamento.

    Raises:
        FileNotFoundError: Se a pasta não existir.
    """
    if not pasta_solicitacao.exists():
        raise FileNotFoundError(
            f"Pasta da solicitação não encontrada: {pasta_solicitacao}"
        )

    pasta_encaminhados = pasta_erp / "Encaminhados"
    pasta_encaminhados.mkdir(parents=True, exist_ok=True)
    destino = pasta_encaminhados / pasta_solicitacao.name

    if destino.exists():
        destino = pasta_encaminhados / f"{pasta_solicitacao.name}_dup"

    shutil.move(str(pasta_solicitacao), str(destino))

    logger.info(
        "Solicitação '%s' encaminhada ao próximo setor → %s",
        pasta_solicitacao.name,
        destino,
    )

    return destino
