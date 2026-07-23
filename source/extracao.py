"""
Módulo de extração de dados do Portal Fake.

Utiliza Playwright para abrir o Portal Fake Soluções Digitais,
clicar em "Novo Cadastro" e extrair os dados do formulário.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright


def extrair_dados() -> dict:
    """
    Abre o Portal Fake, clica em 'Novo Cadastro' e extrai os campos.

    A URL do portal é carregada da variável de ambiente PORTAL_FAKE_URL.
    Se não definida, utiliza o arquivo portal_fake/index.html incluído
    no repositório.

    Returns:
        Dicionário com os dados extraídos do formulário.
    """
    load_dotenv()

    url_portal = os.getenv("PORTAL_FAKE_URL")

    if not url_portal:
        caminho_portal = (
            Path(__file__).resolve().parent.parent
            / "portal_fake"
            / "index.html"
        )
        url_portal = caminho_portal.resolve().as_posix()

    # Garante que caminhos locais tenham o esquema file://
    if not url_portal.startswith(("http://", "https://", "file://")):
        url_portal = f"file://{url_portal}"

    with sync_playwright() as p:
        navegador = p.chromium.launch(headless=True)
        pagina = navegador.new_page()

        # Abrir Portal Fake
        pagina.goto(url_portal)

        # Clicar no botão Novo Cadastro
        pagina.click("#btnNovo")

        # Esperar carregar
        pagina.wait_for_timeout(1000)

        # Extrair os dados
        dados = {
            "nome": pagina.locator("#f_nome").input_value(),
            "sobrenome": pagina.locator("#f_sobrenome").input_value(),
            "cpf": pagina.locator("#f_cpf").input_value(),
            "email": pagina.locator("#f_email").input_value(),
            "telefone": pagina.locator("#f_telefone").input_value(),
            "data_nascimento": pagina.locator("#f_nascimento").input_value(),
            "endereco": pagina.locator("#f_endereco").input_value(),
        }

        print("Dados extraídos:")

        for campo, valor in dados.items():
            print(f"  {campo}: {valor}")

        navegador.close()

        return dados


if __name__ == "__main__":
    extrair_dados()