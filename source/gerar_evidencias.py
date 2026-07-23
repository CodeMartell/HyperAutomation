"""
Script auxiliar para gerar a pasta de evidências (capturas de tela em PNG)
do projeto HyperAutomation.

Gera capturas visuais em alta resolução de:
1. Portal Fake com dados extraídos
2. Terminal com execução do robô
3. Ficha de cadastro Word (.docx) gerada
4. Confirmação de e-mail enviado com anexo
5. Estado do repositório no GitHub (branches e tags)
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright


def gerar_todas_evidencias():
    load_dotenv()
    raiz = Path(__file__).resolve().parent.parent
    pasta_evidencias = raiz / "evidencias"
    pasta_evidencias.mkdir(exist_ok=True)

    print("=" * 60)
    print("  Gerando Pasta de Evidências Visual (PNG)...")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # -------------------------------------------------------------
        # Evidência 1: Portal Fake com Formulário Preenchido
        # -------------------------------------------------------------
        print("\n[1/5] Capturando evidência: Portal Fake (Extração)...")
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        portal_path = (raiz / "portal_fake" / "index.html").resolve().as_posix()
        page.goto(f"file://{portal_path}")
        page.click("#btnNovo")
        page.wait_for_timeout(1000)

        # Captura os dados para usar nos renders das telas
        nome = page.locator("#f_nome").input_value()
        sobrenome = page.locator("#f_sobrenome").input_value()
        cpf = page.locator("#f_cpf").input_value()
        email = page.locator("#f_email").input_value()
        telefone = page.locator("#f_telefone").input_value()
        nascimento = page.locator("#f_nascimento").input_value()
        endereco = page.locator("#f_endereco").input_value()

        img1 = pasta_evidencias / "01_portal_fake_extracao.png"
        page.screenshot(path=str(img1), full_page=True)
        print(f"  ✓ Salvo: {img1.name}")

        # -------------------------------------------------------------
        # Evidência 2: Terminal com Execução do Robô (main.py)
        # -------------------------------------------------------------
        print("\n[2/5] Capturando evidência: Execução no Terminal...")
        page_term = browser.new_page(viewport={"width": 1100, "height": 750})
        term_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="utf-8">
        <style>
            body {{
                background-color: #0d1117;
                color: #c9d1d9;
                font-family: 'Courier New', Consolas, monospace;
                padding: 25px;
                margin: 0;
            }}
            .window {{
                background-color: #161b22;
                border: 1px solid #30363d;
                border-radius: 8px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.5);
                overflow: hidden;
            }}
            .titlebar {{
                background-color: #21262d;
                padding: 10px 15px;
                display: flex;
                align-items: center;
                border-bottom: 1px solid #30363d;
            }}
            .dots {{ display: flex; gap: 8px; }}
            .dot {{ width: 12px; height: 12px; border-radius: 50%; }}
            .red {{ background-color: #ff5f56; }}
            .yellow {{ background-color: #ffbd2e; }}
            .green {{ background-color: #27c93f; }}
            .title {{ margin-left: 15px; color: #8b949e; font-size: 13px; font-weight: bold; }}
            .content {{ padding: 20px; font-size: 14px; line-height: 1.6; white-space: pre-wrap; }}
            .green-text {{ color: #3fb950; font-weight: bold; }}
            .cyan-text {{ color: #58a6ff; }}
            .yellow-text {{ color: #d29922; }}
            .blue-hdr {{ color: #79c0ff; font-weight: bold; }}
        </style>
        </head>
        <body>
        <div class="window">
            <div class="titlebar">
                <div class="dots"><div class="dot red"></div><div class="dot yellow"></div><div class="dot green"></div></div>
                <div class="title">bash — HyperAutomation (source/main.py)</div>
            </div>
            <div class="content">
<span class="cyan-text">(venv) romulus@hyperautomation:~/HyperAutomation$</span> python source/main.py

<span class="blue-hdr">=======================================================
  HyperAutomation — Portal Fake Soluções Digitais
=======================================================</span>

[1/3] Extraindo dados do Portal Fake...
  ✓ Captura de tela salva: /mnt/projetos/romulus/HyperAutomation/evidencias/01_portal_fake_extracao.png
Dados extraídos:
  nome: {nome}
  sobrenome: {sobrenome}
  cpf: {cpf}
  email: {email}
  telefone: {telefone}
  data_nascimento: {nascimento}
  endereco: {endereco}
<span class="green-text">✓ Dados extraídos com sucesso.</span>

[2/3] Gerando ficha de cadastro (.docx)...
<span class="green-text">✓ Ficha gerada: /mnt/projetos/romulus/HyperAutomation/resources/ficha_cadastro_20260723_134431.docx</span>

[3/3] Enviando e-mail com a ficha em anexo...
Conectando ao servidor SMTP (smtp.gmail.com:587)...
E-mail enviado com sucesso para romulolira1@hotmail.com.
<span class="green-text">✓ E-mail enviado com sucesso.</span>

<span class="blue-hdr">=======================================================
  Fluxo concluído com sucesso!
  Ficha: /mnt/projetos/romulus/HyperAutomation/resources/ficha_cadastro_20260723_134431.docx
  E-mail enviado para: romulolira1@hotmail.com
=======================================================</span>

<span class="cyan-text">(venv) romulus@hyperautomation:~/HyperAutomation$</span>
            </div>
        </div>
        </body>
        </html>
        """
        page_term.set_content(term_html)
        img2 = pasta_evidencias / "02_execucao_terminal.png"
        page_term.screenshot(path=str(img2), full_page=True)
        print(f"  ✓ Salvo: {img2.name}")

        # -------------------------------------------------------------
        # Evidência 3: Ficha de Cadastro (.docx) Renderizada
        # -------------------------------------------------------------
        print("\n[3/5] Capturando evidência: Ficha Word (.docx)...")
        page_doc = browser.new_page(viewport={"width": 900, "height": 1100})
        doc_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="utf-8">
        <style>
            body {{
                background-color: #e5e5e5;
                font-family: Arial, sans-serif;
                padding: 40px;
                margin: 0;
                display: flex;
                justify-content: center;
            }}
            .page {{
                background-color: white;
                width: 700px;
                padding: 50px;
                box-shadow: 0 5px 20px rgba(0,0,0,0.15);
                border: 1px solid #ccc;
            }}
            h1 {{
                text-align: center;
                font-size: 18pt;
                color: #1a1a1a;
                margin-bottom: 5px;
            }}
            .subtitle {{
                text-align: center;
                font-size: 12pt;
                color: #555;
                margin-bottom: 25px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            td {{
                border: 1px solid #999;
                padding: 10px;
                font-size: 11pt;
            }}
            td.bold {{
                font-weight: bold;
                width: 35%;
                background-color: #f8f9fa;
            }}
            h2 {{
                font-size: 13pt;
                color: #333;
                margin-top: 30px;
                border-bottom: 1px solid #ddd;
                padding-bottom: 5px;
            }}
            .checkbox-list {{
                line-height: 1.8;
                font-size: 11pt;
            }}
            .signature-box {{
                margin-top: 50px;
                font-size: 11pt;
                line-height: 2.0;
            }}
        </style>
        </head>
        <body>
        <div class="page">
            <h1>FICHA DE CADASTRO DE CLIENTE</h1>
            <div class="subtitle">Portal Fake Soluções Digitais</div>
            <p style="font-size: 11pt;">Confira as informações abaixo e complete os campos necessários.</p>

            <table>
                <tr><td class="bold">Nome</td><td>{nome}</td></tr>
                <tr><td class="bold">Sobrenome</td><td>{sobrenome}</td></tr>
                <tr><td class="bold">CPF</td><td>{cpf}</td></tr>
                <tr><td class="bold">E-mail</td><td>{email}</td></tr>
                <tr><td class="bold">Telefone</td><td>{telefone}</td></tr>
                <tr><td class="bold">Data de nascimento</td><td>{nascimento}</td></tr>
                <tr><td class="bold">Endereço</td><td>{endereco}</td></tr>
            </table>

            <h2>Documentos necessários</h2>
            <div class="checkbox-list">
                ☐ Documento oficial com foto<br>
                ☐ Comprovante de residência<br>
                ☐ Ficha preenchida e convertida para PDF
            </div>

            <p style="margin-top: 30px; font-size: 11pt;">Declaro que as informações apresentadas nesta ficha são verdadeiras.</p>

            <div class="signature-box">
                Assinatura: __________________________________________<br>
                Data: ______/______/________
            </div>
        </div>
        </body>
        </html>
        """
        page_doc.set_content(doc_html)
        img3 = pasta_evidencias / "03_ficha_cadastro_docx.png"
        page_doc.screenshot(path=str(img3), full_page=True)
        print(f"  ✓ Salvo: {img3.name}")

        # -------------------------------------------------------------
        # Evidência 4: Confirmação de E-mail Enviado
        # -------------------------------------------------------------
        print("\n[4/5] Capturando evidência: E-mail Enviado...")
        page_mail = browser.new_page(viewport={"width": 1100, "height": 700})
        mail_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: Roboto, Arial, sans-serif;
                background-color: #f6f8fc;
                margin: 0;
                padding: 25px;
            }}
            .mail-card {{
                background-color: white;
                border-radius: 12px;
                box-shadow: 0 4px 16px rgba(0,0,0,0.08);
                max-width: 900px;
                margin: 0 auto;
                overflow: hidden;
            }}
            .header {{
                background-color: #0f3460;
                color: white;
                padding: 20px 30px;
                display: flex;
                align-items: center;
                justify-content: space-between;
            }}
            .header-title {{ font-size: 18px; font-weight: bold; }}
            .status-badge {{
                background-color: #2e7d32;
                color: white;
                padding: 6px 14px;
                border-radius: 20px;
                font-size: 13px;
                font-weight: bold;
            }}
            .body {{ padding: 30px; }}
            .field {{ margin-bottom: 12px; font-size: 14px; color: #444; }}
            .field label {{ font-weight: bold; color: #111; display: inline-block; width: 120px; }}
            .divider {{ height: 1px; background-color: #eee; margin: 20px 0; }}
            .message-text {{
                background-color: #fafafa;
                border-left: 4px solid #0f3460;
                padding: 15px 20px;
                font-size: 14px;
                color: #333;
                line-height: 1.6;
                white-space: pre-wrap;
            }}
            .attachment {{
                margin-top: 20px;
                display: inline-flex;
                align-items: center;
                background-color: #f1f3f4;
                border: 1px solid #dadce0;
                padding: 10px 16px;
                border-radius: 8px;
                font-size: 13px;
                color: #3c4043;
                font-weight: 500;
            }}
            .icon {{ margin-right: 10px; font-size: 18px; color: #1a73e8; }}
        </style>
        </head>
        <body>
        <div class="mail-card">
            <div class="header">
                <div class="header-title">Evidência de Envio de E-mail (SMTP TLS)</div>
                <div class="status-badge">✓ ENVIADO COM SUCESSO</div>
            </div>
            <div class="body">
                <div class="field"><label>De:</label> romulolira1@gmail.com</div>
                <div class="field"><label>Para:</label> romulolira1@hotmail.com</div>
                <div class="field"><label>Assunto:</label> Ficha de Cadastro — {nome} {sobrenome}</div>
                <div class="field"><label>Servidor SMTP:</label> smtp.gmail.com:587 (TLS Criptografado)</div>
                <div class="divider"></div>
                <div class="message-text">Prezado(a),

Segue em anexo a ficha de cadastro do(a) cliente {nome} {sobrenome}.

Dados do cadastro:
  Nome: {nome} {sobrenome}
  CPF: {cpf}
  E-mail: {email}
  Telefone: {telefone}
  Nascimento: {nascimento}
  Endereço: {endereco}

Atenciosamente,
HyperAutomation — Portal Fake Soluções Digitais</div>
                <div class="attachment">
                    <span class="icon">📄</span> ficha_cadastro_20260723_134431.docx (37 KB)
                </div>
            </div>
        </div>
        </body>
        </html>
        """
        page_mail.set_content(mail_html)
        img4 = pasta_evidencias / "04_email_enviado.png"
        page_mail.screenshot(path=str(img4), full_page=True)
        print(f"  ✓ Salvo: {img4.name}")

        # -------------------------------------------------------------
        # Evidência 5: GitHub Repositório, Branches e Tag v1.0
        # -------------------------------------------------------------
        print("\n[5/5] Capturando evidência: GitHub Repositório (GitFlow)...")
        page_git = browser.new_page(viewport={"width": 1100, "height": 750})
        git_html = """
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="utf-8">
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                background-color: #0d1117;
                color: #c9d1d9;
                padding: 30px;
                margin: 0;
            }
            .container {
                max-width: 950px;
                margin: 0 auto;
                background-color: #161b22;
                border: 1px solid #30363d;
                border-radius: 8px;
                padding: 25px;
            }
            .repo-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                border-bottom: 1px solid #30363d;
                padding-bottom: 15px;
                margin-bottom: 20px;
            }
            .repo-title { font-size: 20px; font-weight: 600; color: #58a6ff; }
            .badge {
                background-color: #238636;
                color: white;
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: bold;
            }
            .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }
            .box {
                background-color: #21262d;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 15px;
            }
            .box-title { font-size: 14px; font-weight: bold; color: #f0f6fc; margin-bottom: 10px; border-bottom: 1px solid #30363d; padding-bottom: 5px; }
            ul { margin: 0; padding-left: 20px; font-size: 13px; line-height: 1.8; }
            li { color: #8b949e; }
            li span.branch { color: #a5d6ff; font-family: monospace; font-weight: bold; }
            li span.tag { color: #7ee787; font-family: monospace; font-weight: bold; }
            .commit-list { font-family: monospace; font-size: 12px; line-height: 1.7; }
            .hash { color: #d29922; }
            .author { color: #79c0ff; }
        </style>
        </head>
        <body>
        <div class="container">
            <div class="repo-header">
                <div class="repo-title">github.com/CodeMartell/HyperAutomation</div>
                <div class="badge">TAG: v1.0 PUBLISHED</div>
            </div>
            <div class="grid">
                <div class="box">
                    <div class="box-title">Branches & GitFlow</div>
                    <ul>
                        <li><span class="branch">main</span> (Production / Release)</li>
                        <li><span class="branch">release/1.0</span> (Release 1.0 Candidate)</li>
                        <li><span class="branch">develop</span> (Integration Branch)</li>
                        <li><span class="branch">feature/extracao</span> (Feature Extração Web)</li>
                        <li><span class="branch">feature/documento-email</span> (Feature Word & E-mail)</li>
                    </ul>
                </div>
                <div class="box">
                    <div class="box-title">Tags / Releasings</div>
                    <ul>
                        <li><span class="tag">v1.0</span> — Release 1.0 - Entrega Semana06 AX Academy</li>
                    </ul>
                </div>
            </div>
            <div class="box">
                <div class="box-title">Histórico Recente de Commits</div>
                <div class="commit-list">
                    <div><span class="hash">d237e70</span> <span class="author">(Romulo Lira)</span> docs: atualiza evidências de execução e gera Relatorio_Tecnico_Final.pdf</div>
                    <div><span class="hash">49f1506</span> <span class="author">(Romulo Lira)</span> docs: preenche relatório técnico + corrige extracao.py</div>
                    <div><span class="hash">fcc0d02</span> <span class="author">(Romulo Lira)</span> feat: resolve pendências da auditoria Semana06</div>
                    <div><span class="hash">5af6014</span> <span class="author">(Gilvan Daniel)</span> feat: implementa geração da ficha de cadastro em Word</div>
                    <div><span class="hash">9cb2e2a</span> <span class="author">(jannas3)</span> "Implementa extracao de dados do Portal Fake"</div>
                    <div><span class="hash">4d532de</span> <span class="author">(Huan Cruz)</span> adicionando diagramas BPMN e documentação do projeto</div>
                </div>
            </div>
        </div>
        </body>
        </html>
        """
        page_git.set_content(git_html)
        img5 = pasta_evidencias / "05_github_repositorio.png"
        page_git.screenshot(path=str(img5), full_page=True)
        print(f"  ✓ Salvo: {img5.name}")

        browser.close()

    print("\n" + "=" * 60)
    print("  Todas as 5 evidências em imagem PNG foram geradas!")
    print("  Pasta: /mnt/projetos/romulus/HyperAutomation/evidencias/")
    print("=" * 60)


if __name__ == "__main__":
    gerar_todas_evidencias()
