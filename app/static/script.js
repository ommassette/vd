// ===== Currency toggle =====
(function () {
  const STORAGE_KEY = 'preferred_currency';
  const stored = localStorage.getItem(STORAGE_KEY);
  const initial = (stored === 'kes' || stored === 'eur') ? stored : 'eur';

  function applyCurrency(currency) {
    document.body.setAttribute('data-currency', currency);

    document.querySelectorAll('[data-currency-toggle]').forEach(btn => {
      const isActive = btn.dataset.currency === currency;
      btn.classList.toggle('is-active', isActive);
      btn.setAttribute('aria-pressed', isActive ? 'true' : 'false');
    });

    document.dispatchEvent(new CustomEvent('currencychange', { detail: { currency } }));
  }

  // Set the initial currency immediately (before first paint of prices)
  applyCurrency(initial);

  document.querySelectorAll('[data-currency-toggle]').forEach(btn => {
    btn.addEventListener('click', () => {
      const currency = btn.dataset.currency;
      localStorage.setItem(STORAGE_KEY, currency);
      applyCurrency(currency);
    });
  });
})();

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
  '.privacy-body',
  '.cs-hero__text',
  '.cs-hero__facts',
  '.cs-section',
  '.cs-video',
  '.cs-cta__inner'
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

// ===== Contact wizard =====
(function () {
  const wizard = document.querySelector('.contact-wizard');
  if (!wizard) return;

  const serviceInput = wizard.querySelector('input[name="service"]');
  const emailInput = wizard.querySelector('input[name="email"]');
  const phoneInput = wizard.querySelector('input[name="phone"]');
  const emailError = wizard.querySelector('[data-email-error]');
  const phoneError = wizard.querySelector('[data-phone-error]');
  const priceList = wizard.querySelector('#priceList');
  const selectedServices = new Map(); // name -> { eur, kes }

  function goToStep(stepNum) {
    const currentStep = wizard.querySelector('.contact-step.is-active');
    const nextStep = wizard.querySelector(`.contact-step[data-step="${stepNum}"]`);
    if (!currentStep || !nextStep || currentStep === nextStep) return;

    wizard.style.height = wizard.offsetHeight + 'px';
    currentStep.classList.remove('is-active');
    nextStep.classList.add('is-active');

    requestAnimationFrame(() => {
      wizard.style.height = nextStep.offsetHeight + 'px';
    });

    setTimeout(() => {
      wizard.style.height = '';
    }, 450);
  }

  // ---- Step 1: multi-select services ----
  const serviceChoices = wizard.querySelectorAll('.contact-step[data-step="1"] .contact-choice');
  const continueBtn = wizard.querySelector('.contact-step[data-step="1"] .contact-form__submit');

  serviceChoices.forEach(choice => {
    choice.addEventListener('click', () => {
      const value = choice.dataset.value;
      const priceEur = choice.dataset.priceEur || '';
      const priceKes = choice.dataset.priceKes || '';

      if (selectedServices.has(value)) {
        selectedServices.delete(value);
        choice.classList.remove('is-selected');
      } else {
        selectedServices.set(value, { eur: priceEur, kes: priceKes });
        choice.classList.add('is-selected');
      }

      serviceInput.value = Array.from(selectedServices.keys()).join(', ');
      if (continueBtn) continueBtn.disabled = selectedServices.size === 0;
    });
  });

  // ---- Price list renderer (reads live currency) ----
  function renderPriceList() {
    if (!priceList) return;

    const currency = document.body.getAttribute('data-currency') || 'eur';

    priceList.innerHTML = '';

    selectedServices.forEach((prices, name) => {
      const li = document.createElement('li');
      li.className = 'contact-price-item';

      const nameSpan = document.createElement('span');
      nameSpan.className = 'contact-price-service';
      nameSpan.textContent = name;

      const priceSpan = document.createElement('span');
      priceSpan.className = 'contact-price-value';
      const value = currency === 'kes' ? prices.kes : prices.eur;
      priceSpan.textContent = value || 'On request';

      li.appendChild(nameSpan);
      li.appendChild(priceSpan);
      priceList.appendChild(li);
    });
  }

  // ---- Continue → populate price list, advance to step 2 ----
  if (continueBtn) {
    continueBtn.addEventListener('click', () => {
      if (selectedServices.size === 0) return;
      renderPriceList();
      goToStep(2);
    });
  }

  // ---- Re-render prices when currency is toggled ----
  document.addEventListener('currencychange', () => {
    if (priceList && priceList.children.length > 0) {
      renderPriceList();
    }
  });

  // ---- Step 2: validation helpers ----
  function normalizePhone(raw) {
    if (!raw) return '';
    let digits = raw.replace(/[^\d+]/g, '');
    if (digits.indexOf('+') > 0) digits = digits.replace(/\+/g, '');
    return digits;
  }

  function isValidPhone(raw) {
    const value = normalizePhone(raw);
    if (!value) return false;
    return /^\+?\d{7,15}$/.test(value);
  }

  function isValidEmail(raw) {
    if (!raw) return false;
    return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(raw.trim());
  }

  function showError(el, message) {
    if (!el) return;
    el.textContent = message;
    el.hidden = false;
  }

  function clearError(el) {
    if (!el) return;
    el.hidden = true;
    el.textContent = '';
  }

  function clearAllErrors() {
    clearError(emailError);
    clearError(phoneError);
    if (emailInput) emailInput.removeAttribute('aria-invalid');
    if (phoneInput) phoneInput.removeAttribute('aria-invalid');
  }

  if (emailInput) emailInput.addEventListener('input', clearAllErrors);
  if (phoneInput) phoneInput.addEventListener('input', clearAllErrors);

  wizard.addEventListener('submit', (e) => {
    clearAllErrors();

    const emailRaw = emailInput ? emailInput.value.trim() : '';
    const phoneRaw = phoneInput ? phoneInput.value.trim() : '';

    // Both empty → blocked
    if (!emailRaw && !phoneRaw) {
      e.preventDefault();
      showError(phoneError, 'Please enter a phone number or an email address.');
      if (phoneInput) {
        phoneInput.setAttribute('aria-invalid', 'true');
        phoneInput.focus();
      }
      return;
    }

    // Email filled but invalid
    if (emailRaw && !isValidEmail(emailRaw)) {
      e.preventDefault();
      showError(emailError, 'Please enter a valid email address.');
      if (emailInput) {
        emailInput.setAttribute('aria-invalid', 'true');
        emailInput.focus();
      }
      return;
    }

    // Phone filled but invalid
    if (phoneRaw && !isValidPhone(phoneRaw)) {
      e.preventDefault();
      showError(phoneError, 'Please enter a valid phone number (7–15 digits).');
      if (phoneInput) {
        phoneInput.setAttribute('aria-invalid', 'true');
        phoneInput.focus();
      }
      return;
    }

    // Normalize phone before submit
    if (phoneInput && phoneRaw) phoneInput.value = normalizePhone(phoneRaw);
  });
})();

// Auto-dismiss flash messages
document.querySelectorAll('.messages .message').forEach(el => {
  setTimeout(() => {
    el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    el.style.opacity = '0';
    el.style.transform = 'translateY(-8px)';
    setTimeout(() => el.remove(), 700);
  }, 5000);
});
// ===== GDPR / DSGVO / RGPD Consent & Backend Logger =====
(function () {
  const CONSENT_KEY = 'valgus_consent_v1';
  const banner = document.getElementById('consentBanner');
  const prefsBox = document.getElementById('consentPrefs');
  const fontsMediaCheckbox = document.getElementById('consentFontsMedia');
  const acceptAllBtn = document.getElementById('consentAcceptAll');
  const rejectAllBtn = document.getElementById('consentRejectAll');
  const customizeBtn = document.getElementById('consentCustomize');
  const savePrefsBtn = document.getElementById('consentSavePrefs');
  const openModalBtn = document.getElementById('openConsentModal');

  if (!banner) return;

  const endpoint = document.body.dataset.consentEndpoint;
  const csrfToken = document.body.dataset.csrfToken;

  function getCookieValue(name) {
    const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    return match ? decodeURIComponent(match[2]) : null;
  }

  function generateId() {
    if (window.crypto && typeof window.crypto.randomUUID === 'function') {
      return window.crypto.randomUUID();
    }
    return 'c_' + Date.now().toString(36) + '_' + Math.random().toString(36).slice(2, 10);
  }

  function readStoredConsent() {
    try {
      const raw = localStorage.getItem(CONSENT_KEY) || getCookieValue(CONSENT_KEY);
      if (!raw) return null;
      return JSON.parse(raw);
    } catch (_) {
      return null;
    }
  }

  function writeStoredConsent(record) {
    const serialized = JSON.stringify(record);
    try {
      localStorage.setItem(CONSENT_KEY, serialized);
    } catch (_) {
      // Fallback to cookie only if storage is blocked
    }
    const maxAge = 60 * 60 * 24 * 180;
    const secureFlag = window.location.protocol === 'https:' ? '; Secure' : '';
    document.cookie = `${CONSENT_KEY}=${encodeURIComponent(serialized)}; path=/; max-age=${maxAge}; SameSite=Lax${secureFlag}`;
  }

  function applyMediaAndFonts(allowed) {
    const existingFont = document.getElementById('google-fonts-raleway');

    if (allowed) {
      if (!existingFont) {
        const pre1 = document.createElement('link');
        pre1.rel = 'preconnect';
        pre1.href = 'https://fonts.googleapis.com';
        document.head.appendChild(pre1);

        const pre2 = document.createElement('link');
        pre2.rel = 'preconnect';
        pre2.href = 'https://fonts.gstatic.com';
        pre2.crossOrigin = 'anonymous';
        document.head.appendChild(pre2);

        const link = document.createElement('link');
        link.id = 'google-fonts-raleway';
        link.rel = 'stylesheet';
        link.href = 'https://fonts.googleapis.com/css2?family=Raleway:wght@200;300;400;600;900&display=swap';
        document.head.appendChild(link);
      }
      document.body.setAttribute('data-fonts-loaded', 'true');
    } else {
      if (existingFont) existingFont.remove();
      document.body.setAttribute('data-fonts-loaded', 'false');
    }
  }

  function sendBackendLog(record, action) {
    if (!endpoint) return;

    const payload = JSON.stringify({
      consent_id: record.consent_id,
      essential: true,
      fonts_and_media: Boolean(record.fonts_and_media),
      action: action,
      page_path: window.location.pathname
    });

    const token = csrfToken || getCookieValue('csrftoken');

    fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': token || ''
      },
      body: payload,
      keepalive: true
    }).catch(() => {
      // Silent fail on network hiccup; consent state remains saved locally
    });
  }

  function saveChoice(fontsAndMedia, action) {
    const existing = readStoredConsent();
    const record = {
      consent_id: (existing && existing.consent_id) ? existing.consent_id : generateId(),
      essential: true,
      fonts_and_media: Boolean(fontsAndMedia),
      updated_at: new Date().toISOString()
    };

    writeStoredConsent(record);
    applyMediaAndFonts(record.fonts_and_media);
    sendBackendLog(record, action);

    if (fontsMediaCheckbox) {
      fontsMediaCheckbox.checked = record.fonts_and_media;
    }
    banner.hidden = true;
    if (prefsBox) prefsBox.hidden = true;
  }

  const current = readStoredConsent();
  if (current) {
    applyMediaAndFonts(Boolean(current.fonts_and_media));
    if (fontsMediaCheckbox) {
      fontsMediaCheckbox.checked = Boolean(current.fonts_and_media);
    }
    banner.hidden = true;
  } else {
    applyMediaAndFonts(false);
    banner.hidden = false;
  }

  if (acceptAllBtn) {
    acceptAllBtn.addEventListener('click', () => saveChoice(true, 'accept_all'));
  }

  if (rejectAllBtn) {
    rejectAllBtn.addEventListener('click', () => saveChoice(false, 'reject_all'));
  }

  if (customizeBtn && prefsBox) {
    customizeBtn.addEventListener('click', () => {
      prefsBox.hidden = !prefsBox.hidden;
    });
  }

  if (savePrefsBtn) {
    savePrefsBtn.addEventListener('click', () => {
      const checked = fontsMediaCheckbox ? Boolean(fontsMediaCheckbox.checked) : false;
      saveChoice(checked, 'custom');
    });
  }

  if (openModalBtn) {
    openModalBtn.addEventListener('click', () => {
      const latest = readStoredConsent();
      if (fontsMediaCheckbox) {
        fontsMediaCheckbox.checked = Boolean(latest && latest.fonts_and_media);
      }
      if (prefsBox) prefsBox.hidden = false;
      banner.hidden = false;
    });
  }
})();