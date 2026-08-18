/* ==========================================================================
   HyperAutomation — Interactive Presentation App Logic (Roteiro 13)
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
    "1. Capa & Identificação (Roteiro 13)",
    "2. Objetivo da Solução Integrada",
    "3. Arquitetura Geral dos 5 Processos",
    "4. Processos 1 e 2 Reutilizados",
    "5. Processo 3 — Setor de Cadastro",
    "6. Processo 4 — Setor de SAC",
    "7. Processo 5 — Setor de Relatórios",
    "8. Integração Real Entre os Processos",
    "9. Logs, Erros, Fallback & Monitoramento",
    "10. Testes Automatizados (pytest & cov)",
    "11. Dockerfile & Containerização",
    "12. GitHub Actions (CI/CD Workflow)",
    "13. Publicação no GHCR",
    "14. Validação da Imagem (Pull & Run)",
    "15. Fluxo Completo da Atividade",
    "16. Resultados Efetivamente Validados",
    "17. Roteiro Prático de Demonstração",
    "18. Conclusão & Encerramento"
  ];

  // Generate dots
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

  // Initial state
  updateSlideState();
});
