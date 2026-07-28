"""
Módulo de leitura de solicitações por e-mail — Processo 1 (Atendimento).

Conecta a uma caixa IMAP, lista e-mails não lidos na pasta INBOX,
baixa os anexos de cada mensagem para a estrutura ERP_Portal_Fake/Downloads/
e retorna uma lista de solicitações com seus metadados.

Justificativa da biblioteca:
    imaplib — biblioteca padrão do Python, sem dependência extra.
    Consistente com o uso de smtplib já adotado no projeto. Suporta
    IMAP4 over SSL (porta 993), compatível com Gmail e Outlook.
    email.policy.default — garante parsing correto de MIME/multipart
    em Python ≥ 3.6.
"""

import email
import imaplib
import logging
import os
import re
from datetime import datetime
from email.header import decode_header
from pathlib import Path

from dotenv import load_dotenv

logger = logging.getLogger(__name__)


def _decodificar_cabecalho(valor: str) -> str:
    """Decodifica um cabeçalho de e-mail com possível encoding MIME."""
    partes = decode_header(valor)
    resultado = []
    for parte, enc in partes:
        if isinstance(parte, bytes):
            resultado.append(parte.decode(enc or "utf-8", errors="replace"))
        else:
            resultado.append(parte)
    return "".join(resultado)


def _sanitizar_nome(nome: str) -> str:
    """Remove caracteres inválidos para nome de pasta/arquivo."""
    return re.sub(r"[^\w\-_. ]", "_", nome).strip()


def receber_solicitacoes(pasta_erp: Path) -> list[dict]:
    """
    Conecta ao servidor IMAP, lê os e-mails não lidos e baixa os anexos.

    Para cada e-mail não lido, cria uma subpasta em:
        ERP_Portal_Fake/Downloads/<YYYYMMDD_HHMMSS_remetente>/

    e salva todos os anexos nela. Marca o e-mail como lido após o processamento.

    Args:
        pasta_erp: Caminho raiz do ERP_Portal_Fake.

    Returns:
        Lista de dicionários, um por solicitação, com as chaves:
            - id_solicitacao (str): nome da subpasta criada
            - remetente (str): e-mail do remetente
            - assunto (str): assunto da mensagem
            - data_recebimento (str): data formatada
            - pasta_downloads (Path): caminho com os anexos baixados
            - anexos (list[str]): nomes dos arquivos baixados

    Raises:
        ValueError: Se as credenciais IMAP não estiverem configuradas.
        imaplib.IMAP4.error: Em caso de falha de conexão/autenticação.
    """
    load_dotenv()

    imap_host = os.getenv("IMAP_HOST", "imap.gmail.com")
    imap_port = int(os.getenv("IMAP_PORT", "993"))
    imap_user = os.getenv("IMAP_USER") or os.getenv("EMAIL_REMETENTE")
    imap_password = os.getenv("IMAP_PASSWORD") or os.getenv("EMAIL_SENHA")

    if not imap_user or not imap_password:
        raise ValueError(
            "Credenciais IMAP não configuradas. "
            "Verifique IMAP_USER e IMAP_PASSWORD no arquivo .env"
        )

    pasta_downloads = pasta_erp / "Downloads"
    pasta_downloads.mkdir(parents=True, exist_ok=True)

    solicitacoes: list[dict] = []

    logger.info("Conectando ao servidor IMAP (%s:%s)...", imap_host, imap_port)

    with imaplib.IMAP4_SSL(imap_host, imap_port) as servidor:
        servidor.login(imap_user, imap_password)
        servidor.select("INBOX")

        _, dados = servidor.search(None, "UNSEEN")
        ids_mensagens = dados[0].split()

        if not ids_mensagens:
            logger.info("Nenhuma mensagem não lida encontrada.")
            return solicitacoes

        logger.info("%d mensagem(ns) não lida(s) encontrada(s).", len(ids_mensagens))

        for msg_id in ids_mensagens:
            try:
                _, dados_msg = servidor.fetch(msg_id, "(RFC822)")
                raw = dados_msg[0][1]
                mensagem = email.message_from_bytes(raw)

                remetente = _decodificar_cabecalho(mensagem.get("From", ""))
                assunto = _decodificar_cabecalho(mensagem.get("Subject", "(sem assunto)"))
                data_recebimento = mensagem.get("Date", "")

                # Extrair apenas o endereço de e-mail do remetente
                match = re.search(r"[\w.\-+]+@[\w.\-]+", remetente)
                email_remetente = match.group(0) if match else remetente

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                id_solicitacao = _sanitizar_nome(
                    f"{timestamp}_{email_remetente}"
                )
                pasta_solicitacao = pasta_downloads / id_solicitacao
                pasta_solicitacao.mkdir(parents=True, exist_ok=True)

                anexos_baixados: list[str] = []

                for parte in mensagem.walk():
                    content_disp = parte.get("Content-Disposition", "")
                    if "attachment" not in content_disp:
                        continue

                    nome_arquivo = parte.get_filename()
                    if not nome_arquivo:
                        continue

                    nome_arquivo = _decodificar_cabecalho(nome_arquivo)
                    nome_arquivo = _sanitizar_nome(nome_arquivo)

                    caminho_arquivo = pasta_solicitacao / nome_arquivo
                    payload = parte.get_payload(decode=True)

                    if payload:
                        caminho_arquivo.write_bytes(payload)
                        anexos_baixados.append(nome_arquivo)
                        logger.info("  ✓ Anexo baixado: %s", nome_arquivo)

                solicitacoes.append(
                    {
                        "id_solicitacao": id_solicitacao,
                        "remetente": email_remetente,
                        "assunto": assunto,
                        "data_recebimento": data_recebimento,
                        "pasta_downloads": pasta_solicitacao,
                        "anexos": anexos_baixados,
                    }
                )

                # Marcar como lido
                servidor.store(msg_id, "+FLAGS", "\\Seen")
                logger.info(
                    "Solicitação recebida de %s com %d anexo(s).",
                    email_remetente,
                    len(anexos_baixados),
                )

            except Exception as erro:
                logger.error(
                    "Erro ao processar mensagem ID %s: %s", msg_id, erro
                )
                continue

    return solicitacoes


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    raiz = Path(__file__).resolve().parent.parent.parent
    erp = raiz / "ERP_Portal_Fake"

    solicitacoes = receber_solicitacoes(erp)
    print(f"\nTotal de solicitações recebidas: {len(solicitacoes)}")
