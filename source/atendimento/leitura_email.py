"""
Módulo de leitura de solicitações por e-mail — Processo 1 (Atendimento).

Conecta a uma caixa IMAP, lista e-mails não lidos na pasta INBOX,
baixa os anexos de cada mensagem para a estrutura ERP_Portal_Fake/Downloads/
e retorna uma lista de solicitações com seus metadados.

Filtros aplicados (configuráveis via .env):
    - Somente e-mails com pelo menos 1 anexo são processados.
    - IMAP_FILTRO_ASSUNTO: se definido, somente e-mails cujo assunto
      contenha essa palavra-chave (case-insensitive) são processados.
      Exemplo: IMAP_FILTRO_ASSUNTO=atendimento

Justificativa da biblioteca:
    imaplib — biblioteca padrão do Python, sem dependência extra.
    Consistente com o uso de smtplib já adotado no projeto. Suporta
    IMAP4 over SSL (porta 993), compatível com Gmail e Outlook.
    Uso de BODY.PEEK[] evita marcar e-mails como lidos antes da
    validação de anexos (RFC822.PEEK não é um comando IMAP válido).
"""

import email
import imaplib
import logging
import os
import re
import socket
from datetime import datetime
from email.header import decode_header
from pathlib import Path

from dotenv import load_dotenv


def _resolver_ipv4(host: str) -> str:
    """
    Resolve o hostname para um endereço IPv4 explícito.

    Evita que o sistema tente IPv6 primeiro quando não há rota IPv6
    disponível na rede local (erro 'No route to host' / errno -3).
    """
    infos = socket.getaddrinfo(host, None, socket.AF_INET)
    if infos:
        return infos[0][4][0]  # primeiro endereço IPv4 encontrado
    return host  # fallback: retorna o host original

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


def _tem_anexo(mensagem: email.message.Message) -> bool:
    """Verifica rapidamente se a mensagem possui ao menos um anexo."""
    for parte in mensagem.walk():
        if "attachment" in parte.get("Content-Disposition", "") and parte.get_filename():
            return True
    return False


def receber_solicitacoes(pasta_erp: Path) -> list[dict]:
    """
    Conecta ao servidor IMAP, lê os e-mails não lidos e baixa os anexos.

    Somente processa e-mails que:
        1. Possuam ao menos 1 anexo.
        2. (Opcional) Tenham a palavra-chave IMAP_FILTRO_ASSUNTO no assunto.

    E-mails sem anexo são ignorados e NÃO são marcados como lidos,
    para não interferir com a caixa do usuário.

    Para cada e-mail aceito, cria uma subpasta em:
        ERP_Portal_Fake/Downloads/<YYYYMMDD_HHMMSS_remetente>/

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
    filtro_assunto = (os.getenv("IMAP_FILTRO_ASSUNTO") or "").strip()
    max_emails = int(os.getenv("IMAP_MAX_EMAILS", "50"))

    if not imap_user or not imap_password:
        raise ValueError(
            "Credenciais IMAP não configuradas. "
            "Verifique IMAP_USER e IMAP_PASSWORD no arquivo .env"
        )

    pasta_downloads = pasta_erp / "Downloads"
    pasta_downloads.mkdir(parents=True, exist_ok=True)

    solicitacoes: list[dict] = []
    ignorados = 0

    logger.info("Conectando ao servidor IMAP (%s:%s)...", imap_host, imap_port)
    if filtro_assunto:
        logger.info("Filtro de assunto (servidor): '%s'", filtro_assunto)
    logger.info("Limite de e-mails por execução: %d", max_emails)

    # Resolve para IPv4 explícito para evitar falha em redes sem rota IPv6
    try:
        imap_host_ipv4 = _resolver_ipv4(imap_host)
        logger.info("Endereço IPv4 resolvido: %s", imap_host_ipv4)
    except socket.gaierror:
        imap_host_ipv4 = imap_host  # fallback: tenta com o hostname mesmo

    with imaplib.IMAP4_SSL(imap_host_ipv4, imap_port) as servidor:
        servidor.login(imap_user, imap_password)
        servidor.select("INBOX")

        # ── Busca no servidor (filtra antes de baixar qualquer coisa) ──────────
        # Se há filtro de assunto, o Gmail filtra no servidor: muito mais rápido
        # do que baixar todos os e-mails e filtrar localmente.
        if filtro_assunto:
            criterio = f'UNSEEN SUBJECT "{filtro_assunto}"'
        else:
            criterio = "UNSEEN"

        _, dados = servidor.search(None, criterio)
        ids_mensagens = dados[0].split()

        total_encontrados = len(ids_mensagens)
        if not ids_mensagens:
            logger.info("Nenhuma mensagem não lida encontrada (critério: %s).", criterio)
            return solicitacoes

        # Pega apenas os mais recentes (últimos N da lista, que são os mais novos)
        if len(ids_mensagens) > max_emails:
            logger.info(
                "%d mensagem(ns) encontrada(s). Processando apenas as %d mais recentes.",
                total_encontrados, max_emails,
            )
            ids_mensagens = ids_mensagens[-max_emails:]
        else:
            logger.info("%d mensagem(ns) encontrada(s) — processando todas.", total_encontrados)

        for msg_id in ids_mensagens:
            try:
                # BODY.PEEK[] lê a mensagem completa sem marcar como lida
                # (RFC822.PEEK não é um comando IMAP válido)
                _, dados_msg = servidor.fetch(msg_id, "(BODY.PEEK[])")
                raw = dados_msg[0][1]
                mensagem = email.message_from_bytes(raw)

                remetente_raw = _decodificar_cabecalho(mensagem.get("From", ""))
                assunto = _decodificar_cabecalho(mensagem.get("Subject", "(sem assunto)"))
                data_recebimento = mensagem.get("Date", "")

                # Extrair apenas o endereço de e-mail do remetente
                match = re.search(r"[\w.\-+]+@[\w.\-]+", remetente_raw)
                email_remetente = match.group(0) if match else remetente_raw

                # ── Filtro 1: assunto (se configurado) ────────────────────────
                if filtro_assunto and filtro_assunto not in assunto.lower():
                    logger.debug(
                        "Ignorado (assunto não corresponde): %s | Assunto: %s",
                        email_remetente, assunto,
                    )
                    ignorados += 1
                    continue

                # ── Filtro 2: obrigatório ter pelo menos 1 anexo ──────────────
                if not _tem_anexo(mensagem):
                    logger.debug(
                        "Ignorado (sem anexo): %s | Assunto: %s",
                        email_remetente, assunto,
                    )
                    ignorados += 1
                    continue

                # ── Aceito: baixar anexos ──────────────────────────────────────
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

                # Marca como lido SOMENTE após aceitar e processar
                servidor.store(msg_id, "+FLAGS", "\\Seen")
                logger.info(
                    "✓ Solicitação aceita de %s com %d anexo(s). Assunto: '%s'",
                    email_remetente,
                    len(anexos_baixados),
                    assunto,
                )

            except Exception as erro:
                logger.error(
                    "Erro ao processar mensagem ID %s: %s", msg_id, erro
                )
                continue

    if ignorados:
        logger.info(
            "%d e-mail(s) ignorado(s) por não ter anexo ou não passar no filtro de assunto.",
            ignorados,
        )

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
