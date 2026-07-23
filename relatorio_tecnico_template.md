# Relatório Técnico Final — HyperAutomation

> **Instruções:** Preencha cada seção abaixo com as informações do seu
> projeto. Após concluir, exporte este documento para PDF para entrega.

---

## 1. Identificação do Projeto

| Campo | Informação |
|---|---|
| **Projeto** | HyperAutomation — Portal Fake Soluções Digitais |
| **Disciplina** | Técnicas de Hyperautomation |
| **Professor(a)** | _(preencher)_ |
| **Turma** | _(preencher)_ |
| **Data de entrega** | _(preencher)_ |

### Integrantes da Equipe

| Nome | Responsabilidade |
|---|---|
| _(preencher)_ | _(ex.: Extração de dados / Playwright)_ |
| _(preencher)_ | _(ex.: Geração de documento / E-mail)_ |
| _(preencher)_ | _(ex.: Modelagem BPMN / Relatório)_ |

---

## 2. Objetivo da Automação

_(Descreva o objetivo geral do projeto: automatizar o cadastro de clientes
do Portal Fake Soluções Digitais, desde a extração de dados até o envio
da ficha por e-mail.)_

---

## 3. Modelagem do Processo (BPMN)

### Diagrama BPMN

_(Insira aqui a imagem do diagrama BPMN — ficha_portal_fake_sd_bpmn.png)_

### Descrição do Fluxo

_(Descreva cada etapa do fluxo modelado no BPMN:)_

1. **Início** — ...
2. **Abrir Portal Fake** — ...
3. **Clicar em Novo Cadastro** — ...
4. **Extrair dados do formulário** — ...
5. **Gerar ficha de cadastro (.docx)** — ...
6. **Enviar e-mail com a ficha** — ...
7. **Fim** — ...

---

## 4. Desenvolvimento da Automação

### Tecnologias Utilizadas

| Tecnologia | Uso |
|---|---|
| Python 3.x | Linguagem principal |
| Playwright | Automação do navegador / extração de dados |
| python-docx | Geração do documento Word |
| smtplib | Envio de e-mail |
| python-dotenv | Gerenciamento de credenciais |

### Extração de Dados (Playwright)

_(Descreva como o script `extracao.py` funciona: abertura do portal,
clique no botão, extração dos campos do formulário.)_

**Campos extraídos:**
- Nome, Sobrenome, CPF, E-mail, Telefone, Data de Nascimento, Endereço

### Código Relevante

_(Insira trechos de código ou prints das funções principais.)_

---

## 5. Documento e Envio de E-mail

### Geração da Ficha (.docx)

_(Descreva como o script `documento_email.py` gera a ficha de cadastro
em formato Word, com tabela de dados e seções formatadas.)_

### Envio de E-mail

_(Descreva como o script `envio_email.py` envia o e-mail com a ficha
em anexo usando smtplib com TLS.)_

### Uso do .env

_(Explique como as credenciais são protegidas usando o arquivo `.env`
com `python-dotenv`, e que o `.env` está no `.gitignore` para não
ser versionado.)_

---

## 6. Versionamento (GitFlow)

### Estratégia de Branches

| Branch | Função |
|---|---|
| `main` | Código estável / release final |
| `develop` | Integração das features |
| `feature/extracao` | Desenvolvimento da extração de dados |
| `feature/documento-email` | Desenvolvimento do documento e e-mail |
| `release/1.0` | Preparação da release |

### Fluxo de Merges

_(Descreva o fluxo: feature → develop → release → main, com a tag v1.0.)_

### Publicação no GitHub

- **Repositório:** https://github.com/CodeMartell/HyperAutomation
- **Tag:** `v1.0`

_(Insira captura de tela do repositório no GitHub.)_

---

## 7. Testes e Evidências

_(Insira capturas de tela para cada item abaixo.)_

### 7.1 Robô em execução

_(Print do terminal executando `python source/main.py`.)_

### 7.2 Dados extraídos

_(Print dos dados extraídos do Portal Fake no console.)_

### 7.3 Ficha de cadastro gerada

_(Print do arquivo .docx aberto no Word/LibreOffice.)_

### 7.4 E-mail recebido

_(Print da caixa de entrada mostrando o e-mail com o anexo.)_

### 7.5 Repositório no GitHub

_(Print do repositório no GitHub mostrando branches, commits e tag.)_

---

## 8. Conclusão

### Dificuldades Encontradas

_(Descreva as dificuldades enfrentadas durante o desenvolvimento.)_

### Melhorias Futuras

_(Sugira melhorias que poderiam ser implementadas, ex.: interface gráfica,
suporte a múltiplos portais, geração de PDF, etc.)_

### Considerações Finais

_(Conclusão geral sobre o aprendizado obtido com o projeto.)_
