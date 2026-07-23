from playwright.sync_api import sync_playwright


def extrair_dados():
    with sync_playwright() as p:
        navegador = p.chromium.launch(headless=False)
        pagina = navegador.new_page()

        # Abrir Portal Fake
        pagina.goto("file:///C:/Users/Turma02/Documents/portal_fake/index.html")

        # Clicar no botão Novo Cadastro
        pagina.click("#btnNovo")

        # Esperar carregar
        pagina.wait_for_timeout(1000)

        # Extrair os dados
        dados = {
            "Nome": pagina.locator("#f_nome").input_value(),
            "Sobrenome": pagina.locator("#f_sobrenome").input_value(),
            "CPF": pagina.locator("#f_cpf").input_value(),
            "E-mail": pagina.locator("#f_email").input_value(),
            "Telefone": pagina.locator("#f_telefone").input_value(),
            "Nascimento": pagina.locator("#f_nascimento").input_value(),
            "Endereco": pagina.locator("#f_endereco").input_value()
        }

        print("Dados extraídos:")

        for campo, valor in dados.items():
            print(f"{campo}: {valor}")

        navegador.close()


if __name__ == "__main__":
    extrair_dados()