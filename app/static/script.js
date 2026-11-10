// ===== Scroll reveal =====
const revealSelectors = [
  '.intro',
  '.brand-name',
  '.about__text',
  '.about__media',
  '.industries__lead',
  '.industries__list',
  '.dark-section__top',
  '.dark-section__title',
  '.footer__nav',
  '.footer__bottom',
  '.services-intro',
  '.services-header__image',
  '.services-header__text',
  '.portfolio-intro',
  '.project__title',
  '.project__strip',
  '.project__desc',
  '.contact-form',
  '.contact-text',
  '.feedback-section__title',
  '.feedback-section__text',
  '.feedback-form',
  '.error-code',
  '.error-message',
  '.error-link',
  '.privacy-header',
  '.privacy-body'
].join(',');

const revealEls = document.querySelectorAll(revealSelectors);

if ('IntersectionObserver' in window && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
  revealEls.forEach(el => el.classList.add('reveal'));

  const io = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

  revealEls.forEach(el => io.observe(el));
} else {
  revealEls.forEach(el => el.classList.add('is-visible'));
}

// ===== Service card dropdown toggles =====
document.querySelectorAll('.service-card__toggle').forEach(btn => {
  btn.addEventListener('click', () => {
    const card = btn.closest('.service-card');
    const isOpen = btn.getAttribute('aria-expanded') === 'true';
    const willOpen = !isOpen;

    btn.setAttribute('aria-expanded', String(willOpen));
    card.querySelector('.service-card__panel').classList.toggle('is-open', willOpen);
    card.classList.toggle('is-reading', willOpen);

    if (!willOpen) {
      const rect = card.getBoundingClientRect();
      if (rect.top < 0) {
        window.scrollTo({
          top: window.scrollY + rect.top,
          behavior: 'smooth'
        });
      }
    }
  });
});

// ===== Testimonials manual carousel =====
(function () {
  const carousel = document.querySelector('.testimonials__carousel');
  if (!carousel) return;

  const testimonials = carousel.querySelectorAll('.testimonial');
  const prevBtn = document.getElementById('prevTestimonial');
  const nextBtn = document.getElementById('nextTestimonial');
  let currentIndex = 0;

  if (!testimonials.length) return;

  testimonials.forEach((t, i) => t.classList.toggle('is-active', i === 0));

  function showTestimonial(index) {
    testimonials.forEach((el, i) => {
      el.classList.toggle('is-active', i === index);
    });
  }

  if (prevBtn) {
    prevBtn.addEventListener('click', function (e) {
      e.preventDefault();
      currentIndex = (currentIndex - 1 + testimonials.length) % testimonials.length;
      showTestimonial(currentIndex);
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener('click', function (e) {
      e.preventDefault();
      currentIndex = (currentIndex + 1) % testimonials.length;
      showTestimonial(currentIndex);
    });
  }
})();
// ===== Image lightbox =====
(function () {
  const lightbox = document.querySelector('.lightbox');
  if (!lightbox) return;

  const imgEl = lightbox.querySelector('.lightbox__img');
  const closeBtn = lightbox.querySelector('.lightbox__close');
  const prevBtn = lightbox.querySelector('.lightbox__prev');
  const nextBtn = lightbox.querySelector('.lightbox__next');

  let currentGroup = [];
  let currentIndex = 0;
  let lastFocused = null;

  function show(index) {
    if (!currentGroup.length) return;
    currentIndex = (index + currentGroup.length) % currentGroup.length;
    const source = currentGroup[currentIndex];
    imgEl.src = source.src;
    imgEl.alt = source.alt || '';
    lightbox.classList.toggle('lightbox--single', currentGroup.length <= 1);
  }

  function open(sourceImg) {
    const strip = sourceImg.closest('.project__strip');
    currentGroup = strip
      ? Array.from(strip.querySelectorAll('img'))
      : [sourceImg];
    const idx = Math.max(0, currentGroup.indexOf(sourceImg));

    lastFocused = document.activeElement;
    lightbox.classList.add('is-open');
    lightbox.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
    show(idx);
    closeBtn.focus();
  }

  function close() {
    lightbox.classList.remove('is-open');
    lightbox.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
    imgEl.src = '';
    imgEl.alt = '';
    if (lastFocused && typeof lastFocused.focus === 'function') {
      lastFocused.focus();
    }
  }

  function prev() { show(currentIndex - 1); }
  function next() { show(currentIndex + 1); }

  document.querySelectorAll('.project__strip img').forEach(img => {
    img.addEventListener('click', () => open(img));
  });

  closeBtn.addEventListener('click', close);
  prevBtn.addEventListener('click', prev);
  nextBtn.addEventListener('click', next);

  // Click on the dark backdrop closes
  lightbox.addEventListener('click', (e) => {
    if (e.target === lightbox) close();
  });

  // Keyboard
  document.addEventListener('keydown', (e) => {
    if (!lightbox.classList.contains('is-open')) return;
    if (e.key === 'Escape') close();
    else if (e.key === 'ArrowLeft') prev();
    else if (e.key === 'ArrowRight') next();
  });
})();