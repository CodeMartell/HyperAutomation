/* ==========================================================================
   HyperAutomation — Interactive Presentation App Logic
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

  // Generate dots
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
    slideTitleIndicator.textContent = slideTitles[currentSlide] || `Slide ${currentSlide + 1}`;
    slideCountIndicator.textContent = `Slide ${currentSlide + 1} de ${totalSlides}`;
    const fillPercent = ((currentSlide + 1) / totalSlides) * 100;
    progressFill.style.width = `${fillPercent}%`;

    // Disable/Enable Nav Buttons
    prevBtn.disabled = currentSlide === 0;
    nextBtn.disabled = currentSlide === totalSlides - 1;
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

  prevBtn.addEventListener('click', prevSlide);
  nextBtn.addEventListener('click', nextSlide);

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
  fullscreenBtn.addEventListener('click', () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().catch(err => console.log(err));
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
      }
    }
  });

  // ── 2. Particle Canvas Animation ───────────────────────────────────────
  const canvas = document.getElementById('bg-canvas');
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

      // Connect near particles
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

  // ── 3. BPMN Interactive Flow Simulator ─────────────────────────────────
  const bpmnSteps = [
    {
      badge: "Etapa 1 / 5",
      title: "Início & Inicialização do Orquestrador",
      body: "O evento de início do BPMN é acionado pela execução do script main.py. O robô carrega as variáveis de ambiente sensíveis do arquivo .env via python-dotenv para obter parâmetros do Portal Fake e credenciais de e-mail."
    },
    {
      badge: "Etapa 2 / 5",
      title: "Navegação & Raspagem de Dados (Playwright)",
      body: "O módulo extracao.py abre uma instância do navegador Chromium em modo headless. Navega até portal_fake/index.html, clica automaticamente no botão '#btnNovo' para preencher o formulário com dados randômicos do cliente."
    },
    {
      badge: "Etapa 3 / 5",
      title: "Extração dos 7 Campos Obrigatórios",
      body: "Utilizando seletores CSS precisos (#f_nome, #f_cpf, #f_email, etc.), o robô extrai os valores informados e captura uma imagem da tela em evidencias/01_portal_fake_extracao.png para fins de auditoria."
    },
    {
      badge: "Etapa 4 / 5",
      title: "Geração da Ficha Oficial (.docx)",
      body: "Os dados coletados são enviados ao módulo documento_email.py. A biblioteca python-docx constrói um documento formatado em Word com tabela Grid, checklist de documentos necessários e campo de assinatura."
    },
    {
      badge: "Etapa 5 / 5",
      title: "Disparo via E-mail SMTP & Encerramento",
      body: "O módulo envio_email.py conecta-se ao servidor SMTP (smtp.gmail.com:587) via TLS, anexa a ficha .docx gerada e envia a mensagem ao destinatário configurado. O processo é finalizado com mensagem de evento de fim."
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
    bpmnBadge.textContent = data.badge;
    bpmnTitle.textContent = data.title;
    bpmnBody.textContent = data.body;

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

  bpmnPrev.addEventListener('click', () => {
    if (currentBpmnStep > 0) {
      currentBpmnStep--;
      updateBpmnView();
    }
  });

  bpmnNext.addEventListener('click', () => {
    if (currentBpmnStep < bpmnSteps.length - 1) {
      currentBpmnStep++;
    } else {
      currentBpmnStep = 0;
    }
    updateBpmnView();
  });

  // ── 4. Code Viewer Tab Switching ───────────────────────────────────────
  const codeSnippets = {
    main: `"""
HyperAutomation — Script Orquestrador.

Integra os três módulos do projeto:
1. Extração de dados do Portal Fake (Playwright)
2. Geração da ficha de cadastro em Word (.docx)
3. Envio do e-mail com a ficha em anexo
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
        corpo="Segue em anexo a ficha de cadastro...",
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
        
        # Salva screenshot de evidência
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

    for campo, valor in dados_cliente.items():
        linha = tabela.add_row().cells
        linha[0].text = campo.capitalize()
        linha[1].text = str(valor)

    documento.save(caminho_documento)
    return caminho_documento`,

    envio: `"""
Módulo de envio de e-mail via smtplib e TLS.
"""
import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from dotenv import load_dotenv

def enviar_email(destinatario: str, assunto: str, corpo: str, caminho_anexo=None):
    load_dotenv()
    remetente = os.getenv("EMAIL_REMETENTE")
    senha = os.getenv("EMAIL_SENHA")
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))

    mensagem = MIMEMultipart()
    mensagem["From"] = remetente
    mensagem["To"] = destinatario
    mensagem["Subject"] = assunto
    mensagem.attach(MIMEText(corpo, "plain", "utf-8"))

    if caminho_anexo:
        with open(caminho_anexo, "rb") as arquivo:
            parte = MIMEBase("application", "octet-stream")
            parte.set_payload(arquivo.read())
        encoders.encode_base64(parte)
        mensagem.attach(parte)

    with smtplib.SMTP(smtp_host, smtp_port) as servidor:
        servidor.starttls()
        servidor.login(remetente, senha)
        servidor.sendmail(remetente, destinatario, mensagem.as_string())`,

    env_example: `# Template de Variáveis de Ambiente (.env.example)

EMAIL_REMETENTE=romulolira1@gmail.com
EMAIL_SENHA=sua_senha_de_app_gerada
EMAIL_DESTINATARIO=romulo.lira@ufam.edu.br
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
PORTAL_FAKE_URL=file:///caminho/para/portal_fake/index.html`
  };

  const codeTabs = document.querySelectorAll('.code-tab');
  const codeContentBlock = document.getElementById('code-content-block');

  function loadCodeTab(key) {
    if (codeSnippets[key]) {
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

  // Initial code load
  loadCodeTab('main');

  // ── 5. RPA Terminal Execution Simulator ────────────────────────────────
  const runRpaBtn = document.getElementById('run-rpa-btn');
  const terminalLog = document.getElementById('terminal-log');
  const terminalStatusText = document.getElementById('terminal-status-text');

  const terminalLines = [
    "=======================================================",
    "  HyperAutomation — Portal Fake Soluções Digitais",
    "=======================================================",
    "",
    "[1/3] Extraindo dados do Portal Fake...",
    "  Iniciando Playwright (Chromium Headless)...",
    "  Navegando para: file:///mnt/projetos/romulus/HyperAutomation/portal_fake/index.html",
    "  Disparando clique no botão #btnNovo...",
    "  Dados extraídos:",
    "    nome: Lucas",
    "    sobrenome: Ferreira",
    "    cpf: 135.028.738-49",
    "    email: lucas.ferreira@email.com",
    "    telefone: (43) 960019-2785",
    "    data_nascimento: 17/04/1989",
    "    endereco: Av. Getúlio Vargas, 1234, Belo Horizonte - MG",
    "  ✓ Captura de tela salva: evidencias/01_portal_fake_extracao.png",
    "✓ Dados extraídos com sucesso.",
    "",
    "[2/3] Gerando ficha de cadastro (.docx)...",
    "  Criando documento Word formatado com python-docx...",
    "  Gerando tabela Grid (7 campos) + Checklist + Assinatura...",
    "✓ Ficha gerada: /resources/ficha_cadastro_20260723_134431.docx",
    "",
    "[3/3] Enviando e-mail com a ficha em anexo...",
    "  Conectando ao servidor SMTP (smtp.gmail.com:587)...",
    "  Iniciando conexão TLS de alta segurança...",
    "  Autenticando remetente via .env (romulolira1@gmail.com)...",
    "  E-mail enviado com sucesso para romulolira1@hotmail.com.",
    "✓ E-mail enviado com sucesso.",
    "",
    "=======================================================",
    "  Fluxo concluído com sucesso!",
    "  Ficha: resources/ficha_cadastro_20260723_134431.docx",
    "  E-mail enviado para: romulolira1@hotmail.com",
    "======================================================="
  ];

  let isSimulating = false;

  runRpaBtn.addEventListener('click', () => {
    if (isSimulating) return;
    isSimulating = true;
    runRpaBtn.disabled = true;
    terminalStatusText.textContent = "Executando Robô RPA...";
    terminalStatusText.style.color = "#ffbd2e";
    terminalLog.textContent = "";

    let lineIdx = 0;

    function typeNextLine() {
      if (lineIdx < terminalLines.length) {
        terminalLog.textContent += terminalLines[lineIdx] + "\n";
        const terminalScreen = document.getElementById('terminal-screen');
        terminalScreen.scrollTop = terminalScreen.scrollHeight;
        lineIdx++;
        setTimeout(typeNextLine, 120);
      } else {
        isSimulating = false;
        runRpaBtn.disabled = false;
        terminalStatusText.textContent = "Fluxo Concluído com Sucesso!";
        terminalStatusText.style.color = "#27c93f";
      }
    }

    typeNextLine();
  });

  // ── 6. Evidence Lightbox Modal ─────────────────────────────────────────
  const galleryCards = document.querySelectorAll('.gallery-card');
  const lightboxModal = document.getElementById('lightbox-modal');
  const lightboxClose = document.getElementById('lightbox-close');
  const lightboxTargetImg = document.getElementById('lightbox-target-img');

  galleryCards.forEach(card => {
    card.addEventListener('click', () => {
      const imgSrc = card.getAttribute('data-img');
      lightboxTargetImg.src = imgSrc;
      lightboxModal.classList.add('active');
    });
  });

  lightboxClose.addEventListener('click', () => {
    lightboxModal.classList.remove('active');
  });

  lightboxModal.addEventListener('click', (e) => {
    if (e.target === lightboxModal) {
      lightboxModal.classList.remove('active');
    }
  });

});
