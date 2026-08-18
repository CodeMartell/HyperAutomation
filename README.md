# HyperAutomation — Portal Fake Soluções Digitais
## Roteiro 13: Integração dos 5 Processos, CI/CD, Containerização & GHCR

![HyperAutomation Pipeline](images/Processo01_Atendimento.png)

Projeto de automação corporativa desenvolvido como atividade da disciplina de **Técnicas de Hyperautomation** (AX Academy / IFAM).

O sistema integra **5 Processos Operacionais** autônomos em uma pipeline encadeada end-to-end, com testes automatizados, logging estruturado, resiliência com fallback, containerização via Docker e pipeline de CI/CD para publicação automática no **GitHub Container Registry (GHCR)**.

---

## 1. Arquitetura Geral do Ecossistema (5 Processos Encadeados)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           FLUXO DE INTEGRAÇÃO                           │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ PROCESSO 1 — Setor de Atendimento                                      │
│ • Leitura de solicitações/anexos via IMAP (ou fallback local)          │
│ • Validação de checklist (Identidade, Comprovante, Ficha)               │
│ • Classificação em Documentos_OK/ ou Documentos_Pendentes/              │
│ • Encaminhamento das solicitações completas para Encaminhados/          │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ PROCESSO 2 — Setor de Organização de Dados                              │
│ • Varredura de pastas de dossiês em Encaminhados/                       │
│ • Extração de dados da Ficha de Cadastro (PDF/OCR)                      │
│ • Validação cadastral (CPF, e-mail, idade mínima 18 anos)               │
│ • Gravação na Planilha Mestra (Planilha_Mestra.xlsx)                    │
│ • Arquivamento da pasta processada em Arquivados/ (idempotência HASH)   │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ PROCESSO 3 — Setor de Cadastro (API Externa)                           │
│ • Recebimento dos dados estruturados do cliente                         │
│ • Validação de campos obrigatórios                                      │
│ • Checagem de duplicidade na base por CPF                               │
│ • Integração com API externa de cadastro (gerando CLI-ID)               │
│ • Mecanismo de Fallback em caso de indisponibilidade da API             │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ PROCESSO 4 — Setor de SAC (Atendimento ao Cliente)                      │
│ • Análise do status retornado pelo Processo 3                           │
│ • Geração de protocolo único de atendimento (SAC-YYYYMMDD-XXXX)         │
│ • Classificação: CONCLUIDO, ALERTA_DUPLICIDADE, PENDENCIA_TECNICA       │
│ • Comunicação por e-mail com o cliente (SMTP real ou simulação segura)   │
│ • Persistência auditável em registro_atendimentos_sac.json              │
│ • Medição de latência (tempo de execução em milissegundos)              │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ PROCESSO 5 — Setor de Relatórios & Gerência                             │
│ • Consolidação dos resultados da execução                               │
│ • Cálculo de KPIs (Total, Sucessos, Duplicidades, Falhas, Taxa % SUC)   │
│ • Emissão de relatório gerencial versionado JSON (timestamped)          │
│ • Atualização do histórico acumulado em historico_relatorios.json       │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                            RESULTADO FINAL                              │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Detalhamento dos Processos

| Processo | Módulo Principal | Responsabilidade | Resiliência & Fallback |
|---|---|---|---|
| **Processo 1 — Atendimento** | `source/atendimento/main_atendimento.py` | Receber solicitações, validar documentação obrigatória e encaminhar dossiês completos. | Fallback para simulação local se serviço de e-mail/Drive estiver inacessível. |
| **Processo 2 — Organização** | `source/organizacao/main_organizacao.py` | Extrair dados da ficha PDF, validar CPF/Email/Idade, atualizar a Planilha Mestra Excel e arquivar. | Idempotência via Hash SHA-256 previne reprocessamento duplicado. |
| **Processo 3 — Cadastro** | `processo3/cadastro.py` | Validar dados, checar duplicidade de CPF e cadastrar cliente na API externa simulada. | `fallback_cadastro()` garante continuidade sem derrubar a pipeline. |
| **Processo 4 — SAC** | `processo4/sac.py` | Gerar protocolo `SAC-YYYYMMDD-XXXX`, enviar notificação ao cliente e gravar histórico JSON. | `fallback_sac()` e canal de contingência retêm comunicação com flag `COMUNICACAO_RETIDA`. |
| **Processo 5 — Relatórios** | `processo5/relatorios.py` | Consolidar métricas operacionais, calcular taxa % de sucesso e salvar relatórios versionados. | `fallback_relatorio()` gera registro auditável de falha caso a carga venha corrompida. |

---

## 3. Pré-requisitos & Instalação

- **Python**: 3.10 ou superior (Recomendado Python 3.14)
- **Docker**: 20.10+ (opcional para execução containerizada)

### Passo a Passo de Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/CodeMartell/HyperAutomation.git
cd HyperAutomation

# 2. Crie e ative o ambiente virtual
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows

# 3. Instale todas as dependências
pip install -r requirements.txt

# 4. Instale o navegador Chromium do Playwright
playwright install chromium
```

---

## 4. Execução Local

### Ponto de Entrada Único (`bot.py` ou `pai.bot.py`)

O projeto possui o orquestrador principal `bot.py` e a entrada de compatibilidade `pai.bot.py`. Ambos executam os 5 processos em sequência:

```bash
# Execução via bot.py (Recomendado)
python bot.py

# Execução via pai.bot.py (Compatibilidade)
python pai.bot.py
```

### Execução de Testes Individuais dos Módulos

```bash
# Simulação end-to-end do Processo 1 & 2
python teste_integracao_definitiva.py

# Teste do Processo 3
python processo3/teste_cadastro.py

# Teste do Processo 4
python processo4/teste_sac.py

# Teste do Processo 5
python processo5/teste_relatorios.py
```

---

## 5. Testes Automatizados & Cobertura

O projeto utiliza `pytest` e `pytest-cov` para execução de testes unitários e de integração de todos os componentes:

### Execução de Testes com Verificação de Sintaxe

```bash
# 1. Validação de Sintaxe de todos os arquivos do projeto
python -m compileall .

# 2. Execução dos testes automatizados (Modo Verboso)
python -m pytest -v

# 3. Execução dos testes com relatório de cobertura de código
python -m pytest -v --cov=. --cov-report=term-missing
```

---

## 6. Containerização com Docker

O projeto possui `Dockerfile` otimizado em imagem Linux slim com Chromium para Playwright.

### Build da Imagem Docker Local

```bash
docker build -t hyperautomation:1.0 .
```

### Execução do Container Docker Local

```bash
docker run --rm hyperautomation:1.0
```

---

## 7. CI/CD no GitHub Actions & Publicação no GHCR

O workflow `.github/workflows/ci-cd.yml` realiza o ciclo completo de Integração e Entrega Contínua:

1. **Pipeline de CI (Testes)**:
   - Dispara em cada `push` ou `pull_request` nas branches `main`, `master` e `develop`.
   - Prepara o ambiente Python, instala dependências e valida sintaxe (`compileall`).
   - Executa a suíte de testes automatizados via `pytest`.
   - **Garantia de Qualidade**: Se qualquer teste falhar, o build Docker e a publicação são abortados imediatamente.

2. **Pipeline de CD (Deploy / GHCR)**:
   - Executa **somente após aprovação dos testes na etapa de CI**.
   - Realiza login no **GitHub Container Registry (GHCR)** via `secrets.GITHUB_TOKEN`.
   - Constrói a imagem Docker e publica em `ghcr.io/${{ github.repository }}:latest`.

### Executando a Imagem Publicada no GHCR

```bash
# 1. Baixar a imagem publicada do repositório no GHCR
docker pull ghcr.io/codemartell/hyperautomation:latest

# 2. Executar o container a partir da imagem do GHCR
docker run --rm ghcr.io/codemartell/hyperautomation:latest
```

---

## 8. Apresentação Técnica & Evidências

A pasta `apresentacao/` contém a **Apresentação Técnica Interativa Web** e o arquivo **PowerPoint**:

- **Apresentação Web Interativa**: Abra `apresentacao/index.html` em qualquer navegador para navegar pelos **18 slides**, interagir com a modelagem BPMN, visualizador de código e simulador de terminal em tempo real.
- **Apresentação PowerPoint**: `apresentacao/Roteiro13_Apresentacao.pptx` contendo o conteúdo corporativo completo.
- **Evidências**: Pasta `evidencias/` contendo screenshots e logs auditáveis (`execucao_bot.log`, `atendimento.log`, `organizacao.log`).

---

## 9. Equipe

| Integrante | Responsabilidade |
|---|---|
| **Romulo Lira** | Orquestração Geral, Integração 1→5, Docker, CI/CD & GHCR |
| **Huan Cruz** | Modelagem BPMN & Visuais de Processo |
| **Gilvan Daniel** | Geração de Documentos Word & Planilha Mestra |
| **Jannas** | Extração Web RPA (Playwright) |

---

## 10. Licença

Projeto acadêmico — **AX Academy / IFAM**.
