"""
Módulo de envio de e-mail com anexo.

Utiliza smtplib com TLS para enviar e-mails de forma segura.
As credenciais são carregadas de um arquivo .env via python-dotenv.
"""

import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from dotenv import load_dotenv


def enviar_email(
    destinatario: str,
    assunto: str,
    corpo: str,
    caminho_anexo: Path | str | None = None,
) -> None:
    """
    Envia um e-mail com anexo opcional.

    Args:
        destinatario: Endereço de e-mail do destinatário.
        assunto: Assunto do e-mail.
        corpo: Corpo do e-mail em texto simples.
        caminho_anexo: Caminho do arquivo a ser anexado (opcional).

    Raises:
        ValueError: Se as credenciais não estiverem configuradas no .env.
        smtplib.SMTPException: Se houver erro na conexão ou envio.
    """
    load_dotenv()

    remetente = os.getenv("EMAIL_REMETENTE")
    senha = os.getenv("EMAIL_SENHA")
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))

    if not remetente or not senha:
        raise ValueError(
            "Credenciais de e-mail não configuradas. "
            "Verifique EMAIL_REMETENTE e EMAIL_SENHA no arquivo .env"
        )

    mensagem = MIMEMultipart()
    mensagem["From"] = remetente
    mensagem["To"] = destinatario
    mensagem["Subject"] = assunto

    mensagem.attach(MIMEText(corpo, "plain", "utf-8"))

    if caminho_anexo:
        caminho_anexo = Path(caminho_anexo)

        if not caminho_anexo.exists():
            raise FileNotFoundError(
                f"Arquivo de anexo não encontrado: {caminho_anexo}"
            )

        with open(caminho_anexo, "rb") as arquivo:
            parte = MIMEBase("application", "octet-stream")
            parte.set_payload(arquivo.read())

        encoders.encode_base64(parte)
        parte.add_header(
            "Content-Disposition",
            f"attachment; filename={caminho_anexo.name}",
        )
        mensagem.attach(parte)

    print(f"Conectando ao servidor SMTP ({smtp_host}:{smtp_port})...")

    with smtplib.SMTP(smtp_host, smtp_port) as servidor:
        servidor.ehlo()
        servidor.starttls()
        servidor.ehlo()
        servidor.login(remetente, senha)
        servidor.sendmail(
            remetente,
            destinatario,
            mensagem.as_string(),
        )

    print(f"E-mail enviado com sucesso para {destinatario}.")


if __name__ == "__main__":
    load_dotenv()

    email_dest = os.getenv("EMAIL_DESTINATARIO", "destinatario@email.com")

    enviar_email(
        destinatario=email_dest,
        assunto="Teste - Ficha de Cadastro",
        corpo="Este é um e-mail de teste do sistema HyperAutomation.",
    )
