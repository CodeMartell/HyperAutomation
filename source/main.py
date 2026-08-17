"""
HyperAutomation — Script Orquestrador.

Integra os três módulos do projeto:
1. Extração de dados do Portal Fake (Playwright)
2. Geração da ficha de cadastro em Word (.docx)
3. Envio do e-mail com a ficha em anexo
"""

import os
import sys

from dotenv import load_dotenv

from source.documento_email import gerar_ficha_cadastro
from source.envio_email import enviar_email
from source.extracao import extrair_dados


def main():
    """Executa o fluxo completo de automação."""
    load_dotenv()

    print("=" * 55)
    print("  HyperAutomation — Portal Fake Soluções Digitais")
    print("=" * 55)

    # ── Etapa 1: Extração de Dados ──────────────────────
    print("\n[1/3] Extraindo dados do Portal Fake...")

    try:
        dados = extrair_dados()
    except Exception as erro:
        print(f"\n✗ Erro na extração: {erro}")
        sys.exit(1)

    print("✓ Dados extraídos com sucesso.\n")

    # ── Etapa 2: Geração do Documento ───────────────────
    print("[2/3] Gerando ficha de cadastro (.docx)...")

    try:
        caminho_ficha = gerar_ficha_cadastro(dados)
    except Exception as erro:
        print(f"\n✗ Erro ao gerar ficha: {erro}")
        sys.exit(1)

    print(f"✓ Ficha gerada: {caminho_ficha}\n")

    # ── Etapa 3: Envio de E-mail ────────────────────────
    print("[3/3] Enviando e-mail com a ficha em anexo...")

    destinatario = os.getenv("EMAIL_DESTINATARIO")

    if not destinatario:
        print(
            "⚠ EMAIL_DESTINATARIO não configurado no .env. "
            "Pulando envio de e-mail."
        )
        print("\nFluxo finalizado (sem envio de e-mail).")
        return

    assunto = (
        f"Ficha de Cadastro — {dados['nome']} {dados['sobrenome']}"
    )
    corpo = (
        f"Prezado(a),\n\n"
        f"Segue em anexo a ficha de cadastro do(a) cliente "
        f"{dados['nome']} {dados['sobrenome']}.\n\n"
        f"Dados do cadastro:\n"
        f"  Nome: {dados['nome']} {dados['sobrenome']}\n"
        f"  CPF: {dados['cpf']}\n"
        f"  E-mail: {dados['email']}\n"
        f"  Telefone: {dados['telefone']}\n"
        f"  Nascimento: {dados['data_nascimento']}\n"
        f"  Endereço: {dados['endereco']}\n\n"
        f"Atenciosamente,\n"
        f"HyperAutomation — Portal Fake Soluções Digitais"
    )

    try:
        enviar_email(
            destinatario=destinatario,
            assunto=assunto,
            corpo=corpo,
            caminho_anexo=caminho_ficha,
        )
    except Exception as erro:
        print(f"\n✗ Erro ao enviar e-mail: {erro}")
        sys.exit(1)

    print("✓ E-mail enviado com sucesso.\n")

    # ── Resumo ──────────────────────────────────────────
    print("=" * 55)
    print("  Fluxo concluído com sucesso!")
    print(f"  Ficha: {caminho_ficha}")
    print(f"  E-mail enviado para: {destinatario}")
    print("=" * 55)


if __name__ == "__main__":
    main()
