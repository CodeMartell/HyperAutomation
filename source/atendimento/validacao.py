"""
Módulo de validação de documentação — Processo 1 (Atendimento).

Verifica se uma solicitação possui todos os documentos obrigatórios.

Critério de "documentação completa" (justificativa):
    São exigidos os mesmos 3 tipos de documento já listados na ficha de
    cadastro Word gerada pelo módulo anterior (documento_email.py), garantindo
    consistência entre os processos:

    1. documento_identidade — RG, CNH ou passaporte (documento oficial c/ foto)
    2. comprovante_residencia — conta de água, luz, extrato bancário, etc.
    3. ficha_cadastro — a própria ficha de cadastro preenchida (PDF)

    A detecção é feita por palavras-chave no nome do arquivo (case-insensitive),
    o que é suficiente para o ambiente simulado e facilmente auditável.
    Em produção, recomenda-se validação adicional de conteúdo via OCR.
"""

import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)

# Palavras-chave por categoria de documento (case-insensitive)
# Um arquivo é aceito em uma categoria se o seu nome contiver
# qualquer uma das palavras-chave dessa categoria.
DOCUMENTOS_OBRIGATORIOS: dict[str, list[str]] = {
    "documento_identidade": [
        "rg",
        "cnh",
        "passaporte",
        "identidade",
        "documento",
        "id",
    ],
    "comprovante_residencia": [
        "comprovante",
        "residencia",
        "residência",
        "conta",
        "extrato",
        "agua",
        "luz",
        "energia",
        "endereco",
    ],
    "ficha_cadastro": [
        "ficha",
        "cadastro",
        "formulario",
        "formulário",
    ],
}

# Extensões de arquivo aceitas por categoria
EXTENSOES_ACEITAS: dict[str, list[str]] = {
    "documento_identidade": [".pdf", ".jpg", ".jpeg", ".png"],
    "comprovante_residencia": [".pdf", ".jpg", ".jpeg", ".png"],
    "ficha_cadastro": [".pdf"],
}


def _arquivo_pertence_categoria(nome_arquivo: str, categoria: str) -> bool:
    """
    Verifica se o nome do arquivo corresponde a uma categoria de documento.

    Args:
        nome_arquivo: Nome do arquivo (sem caminho).
        categoria: Chave da categoria em DOCUMENTOS_OBRIGATORIOS.

    Returns:
        True se o arquivo pertence à categoria, False caso contrário.
    """
    nome_lower = nome_arquivo.lower()
    extensao = Path(nome_arquivo).suffix.lower()

    extensoes_ok = extensao in EXTENSOES_ACEITAS.get(categoria, [])
    if not extensoes_ok:
        return False

    nome_sem_ext = Path(nome_arquivo).stem.lower()
    tokens = re.split(r'[_.\-\s]+', nome_sem_ext)

    for palavra in DOCUMENTOS_OBRIGATORIOS[categoria]:
        if palavra == "id":
            # "id" deve ser um token exato para evitar casar dentro de "residencia"
            if "id" in tokens:
                return True
        elif palavra == "rg":
            # "rg" deve ser um token exato ou prefixo/sufixo de um token (ex: rg_joao, rgjoao)
            if any(t == "rg" or t.startswith("rg") or t.endswith("rg") for t in tokens):
                return True
        else:
            if palavra in nome_lower:
                return True

    return False


def validar_documentacao(
    pasta_solicitacao: Path,
    anexos: list[str],
) -> dict:
    """
    Valida se os documentos obrigatórios estão presentes na solicitação.

    Args:
        pasta_solicitacao: Diretório onde os anexos foram baixados.
        anexos: Lista com os nomes dos arquivos anexados.

    Returns:
        Dicionário com:
            - completa (bool): True se todos os documentos estão presentes
            - presentes (list[str]): categorias encontradas
            - pendentes (list[str]): categorias ausentes
            - detalhes (dict): mapeamento categoria → arquivo encontrado
    """
    presentes: list[str] = []
    pendentes: list[str] = []
    detalhes: dict[str, str | None] = {}

    for categoria in DOCUMENTOS_OBRIGATORIOS:
        encontrado = None

        for nome_arquivo in anexos:
            if _arquivo_pertence_categoria(nome_arquivo, categoria):
                encontrado = nome_arquivo
                break

        detalhes[categoria] = encontrado

        if encontrado:
            presentes.append(categoria)
            logger.info(
                "  ✓ [%s] → %s", categoria, encontrado
            )
        else:
            pendentes.append(categoria)
            logger.warning(
                "  ✗ [%s] → NÃO ENCONTRADO", categoria
            )

    completa = len(pendentes) == 0

    resultado = {
        "completa": completa,
        "presentes": presentes,
        "pendentes": pendentes,
        "detalhes": detalhes,
    }

    if completa:
        logger.info("Documentação COMPLETA — todos os %d documentos encontrados.", len(presentes))
    else:
        logger.warning(
            "Documentação INCOMPLETA — %d/%d documentos presentes. Pendentes: %s",
            len(presentes),
            len(DOCUMENTOS_OBRIGATORIOS),
            ", ".join(pendentes),
        )

    return resultado


if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Teste rápido com arquivos fictícios
    pasta_teste = Path("/tmp/teste_atendimento")
    pasta_teste.mkdir(exist_ok=True)

    # Cenário completo
    print("\n=== Cenário: Documentação COMPLETA ===")
    resultado = validar_documentacao(
        pasta_teste,
        ["rg_frente.pdf", "comprovante_residencia.pdf", "ficha_cadastro.pdf"],
    )
    print(f"Completa: {resultado['completa']}")
    print(f"Pendentes: {resultado['pendentes']}")

    # Cenário incompleto
    print("\n=== Cenário: Documentação INCOMPLETA ===")
    resultado = validar_documentacao(
        pasta_teste,
        ["rg_frente.pdf"],
    )
    print(f"Completa: {resultado['completa']}")
    print(f"Pendentes: {resultado['pendentes']}")

    # Cenário Regressão: Apenas comprovante e ficha, sem documento de identidade
    # (Não deve casar comprovante_residencia em documento_identidade via "id")
    print("\n=== Cenário: FALSO POSITIVO (Apenas comprovante e ficha, sem identidade) ===")
    resultado = validar_documentacao(
        pasta_teste,
        ["comprovante_residencia.pdf", "ficha_cadastro.pdf"],
    )
    print(f"Completa: {resultado['completa']}")
    print(f"Pendentes: {resultado['pendentes']}")
    assert not resultado['completa'], "FALHA: A validação deveria estar incompleta!"
    assert "documento_identidade" in resultado['pendentes'], "FALHA: documento_identidade deveria estar pendente!"
    print("✓ Teste de regressão passou com sucesso!")
