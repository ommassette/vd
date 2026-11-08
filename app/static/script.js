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