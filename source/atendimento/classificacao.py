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
from source.atendimento.google_drive import obter_ou_criar_pasta, upload_arquivo, mover_pasta_drive

logger = logging.getLogger(__name__)


def classificar_solicitacao(
    pasta_solicitacao: Path,
    pasta_erp: Path,
    completa: bool,
    drive_servico=None,
    ids_pastas_drive: dict[str, str] = None,
) -> Path | str:
    """
    Move a pasta da solicitação para Documentos_OK ou Documentos_Pendentes (local ou Google Drive).

    Args:
        pasta_solicitacao: Pasta atual da solicitação (em Downloads/).
        pasta_erp: Raiz do ERP_Portal_Fake.
        completa: True se a documentação está completa.
        drive_servico: Serviço do Google Drive autenticado (opcional).
        ids_pastas_drive: Dicionário com IDs das pastas ERP no Google Drive (opcional).

    Returns:
        Path local do destino se local, ou ID da pasta no Drive se Google Drive for usado.

    Raises:
        FileNotFoundError: Se a pasta da solicitação não existir.
        shutil.Error: Em caso de falha na movimentação.
    """
    if not pasta_solicitacao.exists():
        raise FileNotFoundError(
            f"Pasta da solicitação não encontrada: {pasta_solicitacao}"
        )

    # ── Cenário: Google Drive Integrado ──────────────────────────────────────
    if drive_servico and ids_pastas_drive:
        logger.info("[Drive] Iniciando upload e classificação da solicitação: %s", pasta_solicitacao.name)
        
        # 1. Criar a pasta da solicitação dentro de Downloads/ no Drive
        id_pasta_sol_drive = obter_ou_criar_pasta(
            drive_servico,
            pasta_solicitacao.name,
            ids_pastas_drive["Downloads"]
        )
        
        # 2. Upload de todos os arquivos locais para a pasta no Drive
        for arquivo in pasta_solicitacao.iterdir():
            if arquivo.is_file():
                upload_arquivo(drive_servico, arquivo, id_pasta_sol_drive)
                
        # 3. Mover a pasta no Drive para Documentos_OK ou Documentos_Pendentes
        pasta_destino_nome = "Documentos_OK" if completa else "Documentos_Pendentes"
        id_pasta_destino = ids_pastas_drive[pasta_destino_nome]
        
        mover_pasta_drive(
            drive_servico,
            id_pasta_sol_drive,
            ids_pastas_drive["Downloads"],
            id_pasta_destino
        )
        
        # 4. Remover pasta local temporária para limpar o disco
        shutil.rmtree(pasta_solicitacao)
        logger.info("[Drive] Pasta temporária local limpa: %s", pasta_solicitacao)
        
        return id_pasta_sol_drive

    # ── Cenário: Armazenamento Local ─────────────────────────────────────────
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
    pasta_solicitacao: Path | str,
    pasta_erp: Path,
    drive_servico=None,
    ids_pastas_drive: dict[str, str] = None,
) -> Path | str:
    """
    Move uma solicitação completa para Encaminhados/ (local ou Google Drive).

    Args:
        pasta_solicitacao: Caminho local da pasta (Path) ou ID da pasta no Drive (str).
        pasta_erp: Raiz do ERP_Portal_Fake.
        drive_servico: Serviço do Google Drive autenticado (opcional).
        ids_pastas_drive: Dicionário com IDs das pastas ERP no Google Drive (opcional).

    Returns:
        Novo caminho local ou ID da pasta no Drive.
    """
    # ── Cenário: Google Drive Integrado ──────────────────────────────────────
    if drive_servico and ids_pastas_drive:
        id_pasta_sol_drive = str(pasta_solicitacao)
        logger.info("[Drive] Encaminhando pasta ID %s para a pasta Encaminhados...", id_pasta_sol_drive)
        
        mover_pasta_drive(
            drive_servico,
            id_pasta_sol_drive,
            ids_pastas_drive["Documentos_OK"],
            ids_pastas_drive["Encaminhados"]
        )
        return id_pasta_sol_drive

    # ── Cenário: Armazenamento Local ─────────────────────────────────────────
    pasta_local = Path(pasta_solicitacao)
    if not pasta_local.exists():
        raise FileNotFoundError(
            f"Pasta da solicitação não encontrada: {pasta_local}"
        )

    pasta_encaminhados = pasta_erp / "Encaminhados"
    pasta_encaminhados.mkdir(parents=True, exist_ok=True)
    destino = pasta_encaminhados / pasta_local.name

    if destino.exists():
        destino = pasta_encaminhados / f"{pasta_local.name}_dup"

    shutil.move(str(pasta_local), str(destino))

    logger.info(
        "Solicitação '%s' encaminhada ao próximo setor → %s",
        pasta_local.name,
        destino,
    )

    return destino
