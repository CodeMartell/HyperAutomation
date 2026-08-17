"""
Módulo de resposta ao cliente — Processo 1 (Atendimento).

Envia e-mail de resposta ao remetente da solicitação confirmando o
recebimento e informando se a documentação está completa ou pendente.

Reutiliza envio_email.enviar_email() já implementado no projeto,
garantindo consistência de configuração SMTP e credenciais via .env.
"""

import logging
import sys
from pathlib import Path

# Compatibilidade com execução direta e como módulo do pacote
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from source.envio_email import enviar_email  # noqa: E402

logger = logging.getLogger(__name__)

# Templates de e-mail
_CORPO_COMPLETO = """\
Prezado(a) Cliente,

Recebemos sua solicitação com sucesso e sua documentação foi verificada.

✔ Situação: DOCUMENTAÇÃO COMPLETA

Todos os documentos necessários foram recebidos e sua solicitação foi
encaminhada ao setor responsável para análise.

Documentos recebidos:
{lista_documentos}

Retornaremos em breve com a resposta da sua solicitação.

Atenciosamente,
Setor de Atendimento — Portal Fake Soluções Digitais
HyperAutomation · Processo 1"""

_CORPO_PENDENTE = """\
Prezado(a) Cliente,

Recebemos sua solicitação, porém identificamos que a documentação está
INCOMPLETA.

✘ Situação: DOCUMENTAÇÃO PENDENTE

Documentos recebidos:
{lista_presentes}

Documentos em falta (obrigatórios):
{lista_pendentes}

Por favor, reenvie esta mensagem incluindo os documentos faltantes para
que possamos dar continuidade à sua solicitação.

Documentos obrigatórios:
  1. Documento oficial com foto (RG, CNH ou Passaporte) — formato PDF/JPG
  2. Comprovante de residência — formato PDF/JPG
  3. Ficha de cadastro preenchida — formato PDF

Atenciosamente,
Setor de Atendimento — Portal Fake Soluções Digitais
HyperAutomation · Processo 1"""


def _formatar_lista(itens: list[str]) -> str:
    """Formata uma lista de itens em bullet points."""
    if not itens:
        return "  (nenhum)"
    return "\n".join(f"  • {item}" for item in itens)


def _traduzir_categoria(categoria: str) -> str:
    """Converte o nome da categoria interna para descrição legível."""
    traducoes = {
        "documento_identidade": "Documento oficial com foto (RG/CNH/Passaporte)",
        "comprovante_residencia": "Comprovante de residência",
        "ficha_cadastro": "Ficha de cadastro (PDF)",
    }
    return traducoes.get(categoria, categoria)


def responder_cliente(
    remetente: str,
    assunto_original: str,
    resultado_validacao: dict,
) -> None:
    """
    Envia e-mail de resposta ao cliente com o resultado da validação.

    Args:
        remetente: Endereço de e-mail do cliente (destinatário da resposta).
        assunto_original: Assunto do e-mail recebido (usado no Re:).
        resultado_validacao: Dicionário retornado por validacao.validar_documentacao().

    Raises:
        smtplib.SMTPException: Em caso de falha no envio.
        ValueError: Se as credenciais SMTP não estiverem configuradas.
    """
    completa: bool = resultado_validacao["completa"]
    presentes: list[str] = resultado_validacao["presentes"]
    pendentes: list[str] = resultado_validacao["pendentes"]
    detalhes: dict = resultado_validacao["detalhes"]

    assunto_resposta = f"Re: {assunto_original}"

    if completa:
        documentos_recebidos = [
            f"{_traduzir_categoria(cat)} → {arquivo}"
            for cat, arquivo in detalhes.items()
            if arquivo
        ]
        corpo = _CORPO_COMPLETO.format(
            lista_documentos=_formatar_lista(documentos_recebidos)
        )
        logger.info(
            "Enviando resposta de DOCUMENTAÇÃO COMPLETA para %s", remetente
        )
    else:
        lista_presentes = [
            f"{_traduzir_categoria(cat)} → {detalhes[cat]}"
            for cat in presentes
        ]
        lista_pendentes = [
            _traduzir_categoria(cat) for cat in pendentes
        ]
        corpo = _CORPO_PENDENTE.format(
            lista_presentes=_formatar_lista(lista_presentes),
            lista_pendentes=_formatar_lista(lista_pendentes),
        )
        logger.info(
            "Enviando resposta de DOCUMENTAÇÃO PENDENTE para %s "
            "(faltam: %s)",
            remetente,
            ", ".join(pendentes),
        )

    enviar_email(
        destinatario=remetente,
        assunto=assunto_resposta,
        corpo=corpo,
    )

    logger.info("✓ Resposta enviada para %s.", remetente)
