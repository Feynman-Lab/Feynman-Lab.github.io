(() => {
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

  // Animate only content that enters the viewport. It stays readable without JavaScript.
  if (!reducedMotion.matches && 'IntersectionObserver' in window) {
    const reveal = new IntersectionObserver((entries, observer) => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        entry.target.animate(
          [
            { opacity: 0.55, transform: 'translateY(20px)' },
            { opacity: 1, transform: 'translateY(0)' },
          ],
          { duration: 720, easing: 'cubic-bezier(.16, 1, .3, 1)' },
        );
        observer.unobserve(entry.target);
      }
    }, { threshold: 0.13 });
    document.querySelectorAll('.section > .wrap, .page-content > .wrap, .cta-panel').forEach((node) => reveal.observe(node));
  }

  const canvas = document.querySelector('.hero-field');
  if (!canvas) return;
  const context = canvas.getContext('2d');
  if (!context) return;

  let width = 0;
  let height = 0;
  let visible = true;
  let frameId = 0;
  let points = [];

  function resize() {
    const box = canvas.getBoundingClientRect();
    width = box.width;
    height = box.height;
    const scale = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.round(width * scale);
    canvas.height = Math.round(height * scale);
    context.setTransform(scale, 0, 0, scale, 0, 0);
    points = Array.from({ length: width < 700 ? 18 : 30 }, (_, index) => ({
      x: ((index * 0.61803398875) % 1) * width,
      y: ((index * 0.7548776662) % 1) * height,
      phase: index * 1.37,
      radius: index % 5 === 0 ? 1.5 : 0.9,
    }));
    draw(0);
  }

  function draw(time) {
    context.clearRect(0, 0, width, height);
    const positions = points.map((point) => ({
      x: point.x + (reducedMotion.matches ? 0 : Math.sin(time * 0.00016 + point.phase) * 15),
      y: point.y + (reducedMotion.matches ? 0 : Math.cos(time * 0.00013 + point.phase) * 12),
      radius: point.radius,
    }));
    for (let i = 0; i < positions.length; i += 1) {
      const a = positions[i];
      for (let j = i + 1; j < positions.length; j += 1) {
        const b = positions[j];
        const distance = Math.hypot(a.x - b.x, a.y - b.y);
        if (distance > 150) continue;
        context.strokeStyle = `rgba(152, 190, 239, ${0.12 * (1 - distance / 150)})`;
        context.lineWidth = 0.7;
        context.beginPath();
        context.moveTo(a.x, a.y);
        context.lineTo(b.x, b.y);
        context.stroke();
      }
      context.fillStyle = i % 6 === 0 ? 'rgba(183, 215, 251, .75)' : 'rgba(145, 185, 233, .4)';
      context.beginPath();
      context.arc(a.x, a.y, a.radius, 0, Math.PI * 2);
      context.fill();
    }
  }

  function tick(time) {
    if (!visible || document.hidden || reducedMotion.matches) {
      frameId = 0;
      return;
    }
    draw(time);
    frameId = requestAnimationFrame(tick);
  }

  function refresh() {
    cancelAnimationFrame(frameId);
    frameId = 0;
    if (reducedMotion.matches) draw(0);
    else if (visible && !document.hidden) frameId = requestAnimationFrame(tick);
  }

  resize();
  new ResizeObserver(resize).observe(canvas);
  new IntersectionObserver(([entry]) => {
    visible = entry.isIntersecting;
    refresh();
  }).observe(canvas);
  document.addEventListener('visibilitychange', refresh);
  reducedMotion.addEventListener('change', refresh);
})();
