/* ==========================================================================
   HyperAutomation — Interactive Presentation App Logic (v2.0)
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {

  // ── 1. Slides Controller ───────────────────────────────────────────────
  const slides = document.querySelectorAll('.slide');
  const totalSlides = slides.length;
  let currentSlide = 0;

  const slideTitleIndicator = document.getElementById('slide-title-indicator');
  const slideCountIndicator = document.getElementById('slide-count-indicator');
  const progressFill = document.getElementById('progress-fill');
  const prevBtn = document.getElementById('prev-slide-btn');
  const nextBtn = document.getElementById('next-slide-btn');
  const dotsWrapper = document.getElementById('dots-wrapper');

  const slideTitles = [
    "1. Capa & Identificação Executiva",
    "2. Visão Geral da Arquitetura RPA",
    "3. Modelagem de Processo BPMN 2.0",
    "4. Stack Tecnológica & Código",
    "5. Simulador do Robô em Execução",
    "6. Versionamento & GitFlow",
    "7. Galeria de Evidências & Testes",
    "8. Desafios, Soluções & Roadmap",
    "9. Conclusão & Encerramento"
  ];

  // Generate navigation dots
  dotsWrapper.innerHTML = '';
  slides.forEach((_, idx) => {
    const dot = document.createElement('div');
    dot.classList.add('slide-dot');
    if (idx === 0) dot.classList.add('active');
    dot.addEventListener('click', () => goToSlide(idx));
    dotsWrapper.appendChild(dot);
  });

  const dots = document.querySelectorAll('.slide-dot');

  function updateSlideState() {
    slides.forEach((slide, idx) => {
      if (idx === currentSlide) {
        slide.classList.add('active');
      } else {
        slide.classList.remove('active');
      }
    });

    dots.forEach((dot, idx) => {
      if (idx === currentSlide) {
        dot.classList.add('active');
      } else {
        dot.classList.remove('active');
      }
    });

    // Update Header Progress
    if (slideTitleIndicator) slideTitleIndicator.textContent = slideTitles[currentSlide] || `Slide ${currentSlide + 1}`;
    if (slideCountIndicator) slideCountIndicator.textContent = `Slide ${currentSlide + 1} de ${totalSlides}`;
    if (progressFill) {
      const fillPercent = ((currentSlide + 1) / totalSlides) * 100;
      progressFill.style.width = `${fillPercent}%`;
    }

    // Disable/Enable Nav Buttons
    if (prevBtn) prevBtn.disabled = currentSlide === 0;
    if (nextBtn) nextBtn.disabled = currentSlide === totalSlides - 1;
  }

  function goToSlide(index) {
    if (index >= 0 && index < totalSlides) {
      currentSlide = index;
      updateSlideState();
    }
  }

  function nextSlide() {
    if (currentSlide < totalSlides - 1) {
      currentSlide++;
      updateSlideState();
    }
  }

  function prevSlide() {
    if (currentSlide > 0) {
      currentSlide--;
      updateSlideState();
    }
  }

  if (prevBtn) prevBtn.addEventListener('click', prevSlide);
  if (nextBtn) nextBtn.addEventListener('click', nextSlide);

  // Keyboard navigation
  document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowRight' || e.key === 'Space' || e.key === 'PageDown') {
      nextSlide();
    } else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
      prevSlide();
    }
  });

  // Restart Presentation Button
  const restartBtn = document.getElementById('restart-presentation-btn');
  if (restartBtn) {
    restartBtn.addEventListener('click', () => goToSlide(0));
  }

  // Fullscreen button
  const fullscreenBtn = document.getElementById('fullscreen-btn');
  if (fullscreenBtn) {
    fullscreenBtn.addEventListener('click', () => {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(err => console.log(err));
      } else {
        if (document.exitFullscreen) {
          document.exitFullscreen();
        }
      }
    });
  }

  // ── 2. Particle Canvas Animation ───────────────────────────────────────
  const canvas = document.getElementById('bg-canvas');
  if (canvas) {
    const ctx = canvas.getContext('2d');

    function resizeCanvas() {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    }
    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();

    const particles = [];
    const particleCount = 45;

    for (let i = 0; i < particleCount; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 0.5,
        vy: (Math.random() - 0.5) * 0.5,
        radius: Math.random() * 2 + 1,
        alpha: Math.random() * 0.5 + 0.2
      });
    }

    function drawCanvas() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      for (let i = 0; i < particleCount; i++) {
        let p = particles[i];
        p.x += p.vx;
        p.y += p.vy;

        if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
        if (p.y < 0 || p.y > canvas.height) p.vy *= -1;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(239, 35, 60, ${p.alpha})`;
        ctx.shadowBlur = 10;
        ctx.shadowColor = '#ff4d6d';
        ctx.fill();

        for (let j = i + 1; j < particleCount; j++) {
          let p2 = particles[j];
          let dist = Math.hypot(p.x - p2.x, p.y - p2.y);
          if (dist < 140) {
            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(p2.x, p2.y);
            ctx.strokeStyle = `rgba(217, 4, 41, ${0.15 * (1 - dist / 140)})`;
            ctx.lineWidth = 0.8;
            ctx.stroke();
          }
        }
      }

      requestAnimationFrame(drawCanvas);
    }
    drawCanvas();
  }

  // ── 3. BPMN Interactive Flow Simulator ─────────────────────────────────
  const bpmnSteps = [
    {
      badge: "Etapa 1 / 5",
      title: "Início & Inicialização do Orquestrador",
      body: "O evento de início é acionado pelo orquestrador main.py. O robô carrega as variáveis de ambiente do arquivo .env via python-dotenv para obter parâmetros do Portal Fake e credenciais de e-mail."
    },
    {
      badge: "Etapa 2 / 5",
      title: "Navegação & Raspagem de Dados (Playwright)",
      body: "O módulo extracao.py abre uma instância do navegador Chromium em modo headless, navega até portal_fake/index.html e clica no botão '#btnNovo' para preencher o formulário com dados do cliente."
    },
    {
      badge: "Etapa 3 / 5",
      title: "Extração dos 7 Campos Obrigatórios",
      body: "Utilizando seletores CSS (#f_nome, #f_cpf, #f_email, etc.), o robô extrai os valores informados e salva uma imagem em evidencias/01_portal_fake_extracao.png para auditoria."
    },
    {
      badge: "Etapa 4 / 5",
      title: "Geração da Ficha Oficial (.docx)",
      body: "Os dados coletados são enviados ao módulo documento_email.py. A biblioteca python-docx constrói a ficha formatada em Word com tabela Grid, checklist e campo de assinatura."
    },
    {
      badge: "Etapa 5 / 5",
      title: "Triagem IMAP, Validação & Google Drive",
      body: "O módulo de Atendimento monitora e-mails via IMAP, valida anexos por token/Regex e classifica as solicitações em OK/Pendentes, sincronizando a documentação com o Google Drive."
    }
  ];

  let currentBpmnStep = 0;
  const bpmnBadge = document.getElementById('bpmn-step-badge');
  const bpmnTitle = document.getElementById('bpmn-step-title');
  const bpmnBody = document.getElementById('bpmn-step-body');
  const bpmnNodes = document.querySelectorAll('.bpmn-node-item');
  const bpmnPrev = document.getElementById('bpmn-prev-btn');
  const bpmnNext = document.getElementById('bpmn-next-btn');

  function updateBpmnView() {
    const data = bpmnSteps[currentBpmnStep];
    if (bpmnBadge) bpmnBadge.textContent = data.badge;
    if (bpmnTitle) bpmnTitle.textContent = data.title;
    if (bpmnBody) bpmnBody.textContent = data.body;

    bpmnNodes.forEach((node, idx) => {
      if (idx === currentBpmnStep) {
        node.classList.add('active');
      } else {
        node.classList.remove('active');
      }
    });
  }

  bpmnNodes.forEach(node => {
    node.addEventListener('click', () => {
      currentBpmnStep = parseInt(node.getAttribute('data-step'));
      updateBpmnView();
    });
  });

  if (bpmnPrev) {
    bpmnPrev.addEventListener('click', () => {
      if (currentBpmnStep > 0) {
        currentBpmnStep--;
        updateBpmnView();
      }
    });
  }

  if (bpmnNext) {
    bpmnNext.addEventListener('click', () => {
      if (currentBpmnStep < bpmnSteps.length - 1) {
        currentBpmnStep++;
      } else {
        currentBpmnStep = 0;
      }
      updateBpmnView();
    });
  }

  // ── 4. Code Viewer Tab Switching ───────────────────────────────────────
  const codeSnippets = {
    main: `"""
HyperAutomation — Script Orquestrador Principal.

Integra os módulos da suíte:
1. Extração de dados do Portal Fake (Playwright)
2. Geração da ficha de cadastro em Word (.docx)
3. Envio do e-mail com a ficha em anexo (SMTP TLS)
"""

import os
import sys
from dotenv import load_dotenv

from documento_email import gerar_ficha_cadastro
from envio_email import enviar_email
from extracao import extrair_dados

def main():
    load_dotenv()
    print("=" * 55)
    print("  HyperAutomation — Portal Fake Soluções Digitais")
    print("=" * 55)

    # Etapa 1: Extração
    print("\\n[1/3] Extraindo dados do Portal Fake...")
    dados = extrair_dados()
    print("✓ Dados extraídos com sucesso.\\n")

    # Etapa 2: Geração do Documento
    print("[2/3] Gerando ficha de cadastro (.docx)...")
    caminho_ficha = gerar_ficha_cadastro(dados)
    print(f"✓ Ficha gerada: {caminho_ficha}\\n")

    # Etapa 3: Envio de E-mail
    print("[3/3] Enviando e-mail com a ficha em anexo...")
    destinatario = os.getenv("EMAIL_DESTINATARIO")
    enviar_email(
        destinatario=destinatario,
        assunto=f"Ficha de Cadastro — {dados['nome']} {dados['sobrenome']}",
        corpo="Segue em anexo a ficha de cadastro do cliente...",
        caminho_anexo=caminho_ficha,
    )
    print("✓ E-mail enviado com sucesso.\\n")

if __name__ == "__main__":
    main()`,

    extracao: `"""
Módulo de extração de dados do Portal Fake via Playwright.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

def extrair_dados() -> dict:
    load_dotenv()
    url_portal = os.getenv("PORTAL_FAKE_URL")

    if not url_portal:
        caminho_portal = Path(__file__).resolve().parent.parent / "portal_fake" / "index.html"
        url_portal = caminho_portal.resolve().as_posix()

    if not url_portal.startswith(("http://", "https://", "file://")):
        url_portal = f"file://{url_portal}"

    with sync_playwright() as p:
        navegador = p.chromium.launch(headless=True)
        pagina = navegador.new_page()
        pagina.goto(url_portal)
        pagina.click("#btnNovo")
        pagina.wait_for_timeout(1000)

        dados = {
            "nome": pagina.locator("#f_nome").input_value(),
            "sobrenome": pagina.locator("#f_sobrenome").input_value(),
            "cpf": pagina.locator("#f_cpf").input_value(),
            "email": pagina.locator("#f_email").input_value(),
            "telefone": pagina.locator("#f_telefone").input_value(),
            "data_nascimento": pagina.locator("#f_nascimento").input_value(),
            "endereco": pagina.locator("#f_endereco").input_value(),
        }
        
        caminho_screenshot = Path(__file__).resolve().parent.parent / "evidencias" / "01_portal_fake_extracao.png"
        pagina.screenshot(path=str(caminho_screenshot), full_page=True)
        navegador.close()
        return dados`,

    documento: `"""
Módulo de geração de documento Word (.docx) formatado.
"""
from datetime import datetime
from pathlib import Path
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt

def gerar_ficha_cadastro(dados_cliente: dict, pasta_saida: str = "resources") -> Path:
    raiz_projeto = Path(__file__).resolve().parent.parent
    diretorio_saida = raiz_projeto / pasta_saida
    diretorio_saida.mkdir(parents=True, exist_ok=True)

    data_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_documento = diretorio_saida / f"ficha_cadastro_{data_hora}.docx"

    documento = Document()
    titulo = documento.add_heading("FICHA DE CADASTRO DE CLIENTE", level=1)
    titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER

    tabela = documento.add_table(rows=0, cols=2)
    tabela.style = "Table Grid"

    for campo, valor in [("Nome", dados_cliente["nome"]), ("CPF", dados_cliente["cpf"]), ("E-mail", dados_cliente["email"])]:
        linha = tabela.add_row().cells
        linha[0].text = campo
        linha[1].text = str(valor)
        linha[0].paragraphs[0].runs[0].bold = True

    documento.save(caminho_documento)
    return caminho_documento`,

    leitura_email: `"""
Módulo do Processo 1 — Leitura de E-mails via IMAP.
Refatoração: Filtro de Assunto Case-Insensitive.
"""
import imaplib
import email

def buscar_emails_nao_lidos():
    # ... Conexão IMAP SSL com a caixa de entrada ...
    # Força .lower() em ambas as pontas para contornar falha case-sensitive
    if filtro_assunto and filtro_assunto.lower() not in assunto.lower():
        print(f"Ignorando e-mail: assunto '{assunto}' não contém '{filtro_assunto}'")
        continue`,

    validacao: `"""
Módulo do Processo 1 — Validador de Checklist & Regex.
Refatoração: Isolamento por Tokens contra Bug da Substring 'id'.
"""
import re
from pathlib import Path

def validar_documentos(pasta_downloads: Path) -> dict:
    tokens = re.split(r'[_.\-\s]+', nome_sem_ext)
    
    # Previne que 'residencia.pdf' seja erroneamente classificado como 'id'
    if palavra == "id":
        if "id" in tokens: return True
    elif palavra == "rg":
        if any(t == "rg" or t.startswith("rg") for t in tokens): return True`,

    env_example: `# Template de Variáveis de Ambiente (.env.example)

EMAIL_REMETENTE=romulolira1@gmail.com
EMAIL_SENHA=sua_senha_de_app_aqui
EMAIL_DESTINATARIO=romulo.lira@ufam.edu.br
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
PORTAL_FAKE_URL=`
  };

  const codeTabs = document.querySelectorAll('.code-tab');
  const codeContentBlock = document.getElementById('code-content-block');

  function loadCodeTab(key) {
    if (codeSnippets[key] && codeContentBlock) {
      codeContentBlock.textContent = codeSnippets[key];
    }
  }

  codeTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      codeTabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      loadCodeTab(tab.getAttribute('data-file'));
    });
  });

  loadCodeTab('main');

  // ── 5. RPA Terminal Execution Simulator ────────────────────────────────
  const runSimBtn = document.getElementById('run-sim-btn');
  const clearSimBtn = document.getElementById('clear-sim-btn');
  const terminalOutput = document.getElementById('terminal-screen-output');
  const simStatusIndicator = document.getElementById('sim-status-indicator');

  const terminalLines = [
    "=======================================================",
    "  HyperAutomation — Portal Fake Soluções Digitais",
    "=======================================================",
    "",
    "[1/3] Extraindo dados do Portal Fake (Playwright)...",
    "  ✓ Iniciando Chromium Headless...",
    "  ✓ Navegando até portal_fake/index.html",
    "  ✓ Clique no botão #btnNovo realizado com sucesso.",
    "  Dados extraídos:",
    "    nome: Lucas | sobrenome: Ferreira | cpf: 135.028.738-49",
    "    email: lucas.ferreira@email.com | tel: (43) 960019-2785",
    "  ✓ Captura de tela salva: evidencias/01_portal_fake_extracao.png",
    "",
    "[2/3] Gerando ficha de cadastro (.docx)...",
    "  ✓ Processando modelo python-docx...",
    "  ✓ Ficha gerada: /resources/ficha_cadastro_20260728_160000.docx",
    "",
    "[3/3] Enviando e-mail com a ficha em anexo...",
    "  ✓ Conectando ao servidor SMTP (smtp.gmail.com:587 TLS)...",
    "  ✓ E-mail enviado com sucesso para destinatario@email.com",
    "",
    "=======================================================",
    "  Processo 1 — Setor de Atendimento (Monitor IMAP)",
    "=======================================================",
    "[IMAP] Lendo mensagens com assunto 'Atendimento'...",
    "  ✓ E-mail localizado: joao.silva@exemplo.com",
    "  ✓ Anexos baixados: rg_frente.pdf, comprovante_residencia.pdf, ficha_cadastro.pdf",
    "  ✓ Validador de Checklist (Token Match): DOCUMENTAÇÃO COMPLETA",
    "  ✓ Sincronização Google Drive API: Enviado para Documentos_OK/",
    "  ✓ E-mail automático disparado notificando aprovação do cadastro.",
    "",
    "=======================================================",
    "  FLUXO COMPLETO EXECUTADO COM SUCESSO! (0 ERROS)",
    "======================================================="
  ];

  let isSimulating = false;

  if (runSimBtn && terminalOutput) {
    runSimBtn.addEventListener('click', () => {
      if (isSimulating) return;
      isSimulating = true;
      runSimBtn.disabled = true;

      if (simStatusIndicator) {
        simStatusIndicator.innerHTML = '<span style="color:#ffbd2e;font-weight:bold;">● Executando Robô RPA...</span>';
      }

      terminalOutput.textContent = "";
      let lineIdx = 0;

      function typeNextLine() {
        if (lineIdx < terminalLines.length) {
          terminalOutput.textContent += terminalLines[lineIdx] + "\n";
          terminalOutput.scrollTop = terminalOutput.scrollHeight;
          lineIdx++;
          setTimeout(typeNextLine, 100);
        } else {
          isSimulating = false;
          runSimBtn.disabled = false;
          if (simStatusIndicator) {
            simStatusIndicator.innerHTML = '<span style="color:#27c93f;font-weight:bold;">✓ Concluído com Sucesso!</span>';
          }
        }
      }

      typeNextLine();
    });
  }

  if (clearSimBtn && terminalOutput) {
    clearSimBtn.addEventListener('click', () => {
      terminalOutput.textContent = 'Pressione "Executar Robô RPA" para iniciar a simulação...';
      if (simStatusIndicator) {
        simStatusIndicator.innerHTML = '<span class="status-dot-idle"></span> Aguardando Disparo';
      }
    });
  }

});

// Global Modal Functions for Lightbox
function openModal(src, captionText) {
  const modal = document.getElementById('img-modal');
  const modalImg = document.getElementById('modal-img-target');
  const modalCaption = document.getElementById('modal-caption-target');
  
  if (modal && modalImg && modalCaption) {
    modalImg.src = src;
    modalCaption.textContent = captionText;
    modal.classList.add('active');
  }
}

function closeModal() {
  const modal = document.getElementById('img-modal');
  if (modal) {
    modal.classList.remove('active');
  }
}
