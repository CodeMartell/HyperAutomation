# HyperAutomation — Portal Fake Soluções Digitais

Projeto de automação desenvolvido como atividade da **Semana 06** do módulo
de Técnicas de Hyperautomation (AX Academy / IFAM).

O sistema automatiza o processo de cadastro de clientes do Portal Fake
Soluções Digitais: extrai dados do formulário web, gera uma ficha de
cadastro em Word e envia por e-mail.

## BPMN — Modelagem do Processo

![Portal Fake](images/ficha_portal_fake_sd_bpmn.png)

## Pré-requisitos

- Python 3.10 ou superior
- Google Chrome / Chromium instalado

## Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/CodeMartell/HyperAutomation.git
cd HyperAutomation

# 2. Crie e ative o ambiente virtual
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Instale os navegadores do Playwright
playwright install chromium
```

## Configuração

Copie o arquivo de exemplo e preencha com suas credenciais:

```bash
cp .env.example .env
```

Edite o `.env` com os dados do seu servidor de e-mail:

| Variável | Descrição |
|---|---|
| `EMAIL_REMETENTE` | romulolira1@gmail.com |
| `EMAIL_SENHA` | Senha de app (não a senha principal) |
| `EMAIL_DESTINATARIO` | romulo.lira@ufam.edu.br |
| `SMTP_HOST` | Servidor SMTP (padrão: `smtp.gmail.com`) |
| `SMTP_PORT` | Porta SMTP (padrão: `587`) |
| `PORTAL_FAKE_URL` | _(opcional)_ URL personalizada do portal |

> **Nota:** Para Gmail, é necessário gerar uma
> [Senha de App](https://myaccount.google.com/apppasswords).

## Execução

```bash
python source/main.py
```

O script executa automaticamente as três etapas:
1. **Extração** — Abre o Portal Fake e extrai os dados do formulário
2. **Documento** — Gera a ficha de cadastro em `.docx` na pasta `resources/`
3. **E-mail** — Envia a ficha como anexo para o destinatário configurado

## Estrutura do Projeto

```
HyperAutomation/
├── .env.example              # Template de variáveis de ambiente
├── .gitignore
├── README.md
├── requirements.txt          # Dependências Python
├── images/
│   ├── ficha_portal_fake_sd_bpmn.drawio   # BPMN editável
│   └── ficha_portal_fake_sd_bpmn.png      # BPMN exportado
├── portal_fake/
│   └── index.html            # Mock do Portal Fake
├── resources/
│   └── ficha_cadastro_*.docx # Fichas geradas
└── source/
    ├── main.py               # Script orquestrador
    ├── extracao.py            # Extração de dados (Playwright)
    ├── documento_email.py     # Geração da ficha Word
    └── envio_email.py         # Envio de e-mail (smtplib)
```

## Equipe

| Integrante | Responsabilidade |
|---|---|
| _(preencher)_ | _(preencher)_ |

## Licença

Projeto acadêmico — AX Academy / IFAM.
