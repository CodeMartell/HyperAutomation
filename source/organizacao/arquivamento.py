"""
Módulo de arquivamento e cálculo de hash — Processo 2 (Organização de Dados).

Calcula hashes de arquivos para controle de idempotência e move os dossiês processados para a pasta Arquivados.
"""

import hashlib
import logging
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)

def calcular_hash_arquivo(caminho_arquivo: Path) -> str:
    """
    Calcula o hash SHA-256 de um arquivo local.
    """
    sha256 = hashlib.sha256()
    try:
        with open(caminho_arquivo, "rb") as f:
            for bloco in iter(lambda: f.read(4096), b""):
                sha256.update(bloco)
        return sha256.hexdigest()
    except Exception as e:
        logger.error("Erro ao calcular hash do arquivo %s: %s", caminho_arquivo.name, e)
        raise e

def arquivar_pasta_local(pasta_solicitacao: Path, pasta_arquivados_base: Path) -> Path:
    """
    Move a pasta da solicitação de forma local para a pasta Arquivados.
    Evita colisões adicionando sufixos se necessário.
    
    Returns:
        Path: Caminho final da pasta no destino.
    """
    if not pasta_solicitacao.exists():
        raise FileNotFoundError(f"Pasta de solicitação não encontrada: {pasta_solicitacao}")

    pasta_arquivados_base.mkdir(parents=True, exist_ok=True)
    destino = pasta_arquivados_base / pasta_solicitacao.name

    contador = 1
    nome_original = pasta_solicitacao.name
    while destino.exists():
        destino = pasta_arquivados_base / f"{nome_original}_dup{contador}"
        contador += 1

    shutil.move(str(pasta_solicitacao), str(destino))
    logger.info("Pasta '%s' arquivada localmente em '%s'", pasta_solicitacao.name, destino.name)
    return destino

def arquivar_pasta_drive(servico, folder_id: str, id_pasta_origem: str, id_pasta_arquivados: str) -> None:
    """
    Move uma pasta no Google Drive da pasta de entrada para a pasta de Arquivados.
    Reutiliza a lógica do módulo de atendimento para atualizar parents.
    """
    from source.atendimento.google_drive import mover_pasta_drive
    
    logger.info("[Drive] Movendo pasta ID %s para a pasta Arquivados...", folder_id)
    mover_pasta_drive(
        servico=servico,
        folder_id=folder_id,
        old_parent_id=id_pasta_origem,
        new_parent_id=id_pasta_arquivados
    )
