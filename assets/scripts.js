// =====================================================
// Gemeinsame Helfer
// =====================================================
const $id = (id) => document.getElementById(id);
const $qs = (sel, root = document) => root.querySelector(sel);
const on = (el, ev, fn, opts) => el && el.addEventListener(ev, fn, opts);

// defensives console-Wrapper
const warn = (...args) => console.warn('[scripts.js]', ...args);

// =====================================================
// Start, wenn DOM bereit ist
// =====================================================
document.addEventListener('DOMContentLoaded', async () => {
  try {
    await initPartials();
  } catch (e) {
    warn('Fehler in initPartials:', e);
  }

  try {
    await initRecipeSearch();
  } catch (e) {
    warn('Fehler in initRecipeSearch:', e);
  }

  try {
    initBootstrapMultiCardCarousel();
  } catch (e) {
    warn('Fehler in initBootstrapMultiCardCarousel:', e);
  }

  try {
    initCustomMarqueeCarousel();
  } catch (e) {
    warn('Fehler in initCustomMarqueeCarousel:', e);
  }

  try {
    await initRecipeSections();
  } catch (e) {
    warn('Fehler in initRecipeSections:', e);
  }
});

// =====================================================
// Partials (Navbar & Footer) nur laden, wenn Ziel existiert
// =====================================================
async function initPartials() {
  const loadPartial = async (id, url) => {
    const el = $id(id);
    if (!el) return;

    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`${url} konnte nicht geladen werden. Status: ${response.status}`);
    }

    const html = await response.text();
    el.innerHTML = html;
  };

  const jobs = [];

  if ($id('site-navbar')) {
    jobs.push(
      loadPartial('site-navbar', '../../partials/navbar.html').catch(err =>
        warn('Fehler beim Laden von ../../partials/navbar.html:', err)
      )
    );
  }

  if ($id('site-footer')) {
    jobs.push(
      loadPartial('site-footer', '../../partials/footer.html').catch(err =>
        warn('Fehler beim Laden von ../../partials/footer.html:', err)
      )
    );
  }

  await Promise.all(jobs);
}

// =====================================================
// Navbar-Rezeptsuche
// WICHTIG: läuft erst NACH initPartials()
// =====================================================
async function initRecipeSearch() {
  const form = $id('recipeSearchForm');
  const input = $id('recipeSearchInput');
  const suggestionsBox = $id('recipeSuggestions');

  if (!form || !input || !suggestionsBox) {
    return;
  }

  const RECIPES_JSON = siteUrl('recipes.json');
  const SEARCH_PAGE = siteUrl('search.html');
  const FALLBACK_IMG = 'https://ik.imagekit.io/o9fejv2tr/RecsWeb%20Icons/image_not_found.png?updatedAt=1756760226935';

  let recipes = [];

  const normalizeText = (text = '') =>
    String(text)
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '');

  const hideSuggestions = () => {
    suggestionsBox.innerHTML = '';
    suggestionsBox.classList.add('d-none');
  };

  const showSuggestions = (matches) => {
    suggestionsBox.innerHTML = '';

    if (!matches.length) {
      const empty = document.createElement('div');
      empty.className = 'recipe-suggestion-empty';
      empty.textContent = 'No matching recipes';
      suggestionsBox.appendChild(empty);
      suggestionsBox.classList.remove('d-none');
      return;
    }

    for (const recipe of matches) {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'recipe-suggestion-item';
      button.dataset.title = recipe.title || '';

      const img = document.createElement('img');
      img.src = recipe.image && recipe.image !== 'N/A' ? recipe.image : FALLBACK_IMG;
      img.alt = recipe.title || 'Rezeptbild';

      const span = document.createElement('span');
      span.textContent = recipe.title || 'Ohne Titel';

      button.append(img, span);
      suggestionsBox.appendChild(button);
    }

    suggestionsBox.classList.remove('d-none');
  };

  try {
    const response = await fetch(RECIPES_JSON);
    if (!response.ok) {
      throw new Error(`recipes.json konnte nicht geladen werden. Status: ${response.status}`);
    }

    recipes = await response.json();
    if (!Array.isArray(recipes)) recipes = [];
  } catch (error) {
    console.error('Fehler beim Laden der Rezepte für die Suche:', error);
    return;
  }

  input.addEventListener('input', () => {
    const query = input.value.trim();
    const normalizedQuery = normalizeText(query);

    if (normalizedQuery.length < 1) {
      hideSuggestions();
      return;
    }

    const matches = recipes
      .filter(recipe => normalizeText(recipe?.title || '').includes(normalizedQuery))
      .slice(0, 8);

    showSuggestions(matches);
  });

  suggestionsBox.addEventListener('click', (event) => {
    const button = event.target.closest('.recipe-suggestion-item');
    if (!button) return;

    const selectedTitle = button.dataset.title || '';
    input.value = selectedTitle;
    hideSuggestions();

    window.location.href = `${SEARCH_PAGE}?q=${encodeURIComponent(selectedTitle)}`;
  });

  form.addEventListener('submit', (event) => {
    event.preventDefault();

    const query = input.value.trim();
    if (!query) {
      hideSuggestions();
      return;
    }

    window.location.href = `${SEARCH_PAGE}?q=${encodeURIComponent(query)}`;
  });

  document.addEventListener('click', (event) => {
    if (!form.contains(event.target)) {
      hideSuggestions();
    }
  });

  input.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      hideSuggestions();
    }
  });
}

// =====================================================
// Bootstrap Multi-Card Carousel (optional)
// erwartet Markup mit #carouselExampleControls
// =====================================================
function initBootstrapMultiCardCarousel() {
  const rootSel = '#carouselExampleControls';
  const root = $qs(rootSel);
  if (!root) return;

  if (typeof window.bootstrap === 'undefined' || !bootstrap.Carousel) {
    warn('Bootstrap nicht gefunden; überspringe Multi-Card Carousel.');
    return;
  }

  const isDesktop = window.matchMedia('(min-width: 768px)').matches;

  if (isDesktop) {
    const carouselInner = $qs(`${rootSel} .carousel-inner`);
    const firstItem = $qs(`${rootSel} .carousel-item`);
    if (!carouselInner || !firstItem) {
      warn('Carousel-Inhalt unvollständig; überspringe Logik.');
      return;
    }

    new bootstrap.Carousel(root, {
      interval: false,
      wrap: false,
    });

    const getCardWidth = () => {
      const w = firstItem.offsetWidth;
      return w > 0 ? w : firstItem.getBoundingClientRect().width || 0;
    };

    let scrollPosition = 0;

    const recalcAndClamp = () => {
      const carouselWidth = carouselInner.scrollWidth || 0;
      const cardWidth = getCardWidth();
      const visibleCards = 4;
      const maxScroll = Math.max(0, carouselWidth - cardWidth * visibleCards);
      scrollPosition = Math.min(scrollPosition, maxScroll);
      return { carouselWidth, cardWidth, maxScroll, visibleCards };
    };

    const btnNext = $qs(`${rootSel} .carousel-control-next`);
    const btnPrev = $qs(`${rootSel} .carousel-control-prev`);

    const nextSlide = () => {
      const { cardWidth, maxScroll } = recalcAndClamp();
      if (cardWidth <= 0) return;
      if (scrollPosition < maxScroll) {
        scrollPosition += cardWidth;
      } else {
        scrollPosition = 0;
      }
      carouselInner.scroll({ left: scrollPosition, behavior: 'smooth' });
    };

    const prevSlide = () => {
      const { cardWidth, maxScroll } = recalcAndClamp();
      if (cardWidth <= 0) return;
      if (scrollPosition > 0) {
        scrollPosition -= cardWidth;
      } else {
        scrollPosition = maxScroll;
      }
      carouselInner.scroll({ left: scrollPosition, behavior: 'smooth' });
    };

    on(btnNext, 'click', nextSlide);
    on(btnPrev, 'click', prevSlide);

    let autoSlideInterval = null;

    const startAutoSlide = () => {
      stopAutoSlide();
      autoSlideInterval = setInterval(nextSlide, 2000);
    };

    const stopAutoSlide = () => {
      clearInterval(autoSlideInterval);
      autoSlideInterval = null;
    };

    startAutoSlide();

    on(root, 'mouseenter', stopAutoSlide);
    on(root, 'mouseleave', startAutoSlide);

    on(window, 'resize', () => {
      recalcAndClamp();
      carouselInner.scroll({ left: scrollPosition });
      stopAutoSlide();
      startAutoSlide();
    });
  } else {
    root.classList.add('slide');
  }
}

// =====================================================
// Custom „Marquee"-Carousel (optional)
// erwartet: #miTrack, #btnNext, #btnPrev
// =====================================================
function initCustomMarqueeCarousel() {
  const track = $id('miTrack');
  const btnNext = $id('btnNext');
  const btnPrev = $id('btnPrev');

  if (!track) return;

  let animating = false;

  const getStep = () => {
    if (!track.children || track.children.length === 0) return 0;

    const first = track.children[0];
    const rect = first.getBoundingClientRect();
    let gap = 0;

    if (track.children.length > 1) {
      const second = track.children[1];
      gap = second.getBoundingClientRect().left - rect.right;
    }
    return (rect.width || 0) + (gap || 0);
  };

  const animateTo = (x, cb) => {
    track.style.transition = 'transform .45s ease';
    track.style.transform = `translateX(${x}px)`;
    const done = () => {
      track.style.transition = 'none';
      track.style.transform = 'translateX(0px)';
      track.removeEventListener('transitionend', done);
      cb && cb();
      animating = false;
    };
    track.addEventListener('transitionend', done, { once: true });
  };

  const next = () => {
    if (animating) return;
    const step = getStep();
    if (step <= 0) return;
    animating = true;
    animateTo(-step, () => {
      if (track.firstElementChild) {
        track.appendChild(track.firstElementChild);
      }
    });
  };

  const prev = () => {
    if (animating) return;
    const step = getStep();
    if (step <= 0) return;
    animating = true;
    track.style.transition = 'none';
    if (track.lastElementChild) {
      track.insertBefore(track.lastElementChild, track.firstElementChild);
    }
    track.style.transform = `translateX(${-step}px)`;
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        animateTo(0);
      });
    });
  };

  on(btnNext, 'click', next);
  on(btnPrev, 'click', prev);

  const AUTOPLAY_MS = 2000;
  let autoplayId = null;

  const startAutoplay = () => {
    stopAutoplay();
    if (track.children && track.children.length > 1) {
      autoplayId = setInterval(() => {
        if (!animating) next();
      }, AUTOPLAY_MS);
    }
  };

  const stopAutoplay = () => {
    if (autoplayId) {
      clearInterval(autoplayId);
      autoplayId = null;
    }
  };

  startAutoplay();

  on(track, 'mouseenter', stopAutoplay);
  on(track, 'mouseleave', startAutoplay);

  let startX = 0;
  on(track, 'pointerdown', (e) => {
    startX = e.clientX ?? 0;
    stopAutoplay();
  }, { passive: true });

  on(track, 'pointerup', (e) => {
    const dx = (e.clientX ?? 0) - startX;
    if (Math.abs(dx) > 30) {
      dx < 0 ? next() : prev();
    }
    setTimeout(startAutoplay, 1000);
  });

  on(window, 'resize', () => {
    track.style.transition = 'none';
    track.style.transform = 'translateX(0px)';
    stopAutoplay();
    startAutoplay();
  });
}

// =====================================================
// Recipe Carousel Initialization
// =====================================================
async function initRecipeSections() {
  const sections = Array.from(document.querySelectorAll('section[data-category], section[data-categorie]'));
  if (!sections.length) return;

  const RECIPES_JSON_URL = siteUrl('recipes.json');
  const FALLBACK_IMG = 'https://ik.imagekit.io/o9fejv2tr/RecsWeb%20Icons/image_not_found.png?updatedAt=1756760226935';

  const toKey = (s) => (s || '').toString().trim().toLowerCase();

  const pickCountryFlag = (categories = []) => {
    for (const c of categories) {
      const k = toKey(c);
      if (COUNTRY_FLAGS[k]) return COUNTRY_FLAGS[k];
    }
    return null;
  };

  const buildBadges = (categories = []) => {
    const frag = document.createDocumentFragment();
    const seen = new Set();

    for (const raw of categories) {
      const k = toKey(raw);
      if (seen.has(k)) continue;
      seen.add(k);

      const conf = CATEGORY_BADGES[k];
      const label = (conf && conf.label) ? conf.label : k;

      const span = document.createElement('span');
      span.className = `badge ${conf ? conf.cls : 'bg-light text-dark border'} me-1 mb-1`;
      span.textContent = label;
      frag.appendChild(span);
    }

    return frag;
  };

  const buildCard = (recipe) => {
    const a = document.createElement('a');
    a.href = recipe.file || '#';
    a.className = 'text-decoration-none text-dark';

    const card = document.createElement('div');
    card.className = 'card h-100';

    const img = document.createElement('img');
    img.className = 'card-img-top';
    img.src = (recipe.image && recipe.image !== 'N/A') ? recipe.image : FALLBACK_IMG;
    img.alt = recipe.title || 'Rezeptbild';

    const body = document.createElement('div');
    body.className = 'card-body';

    const h4 = document.createElement('h4');
    h4.className = 'card-title mb-2';
    h4.textContent = recipe.title || 'Rezept';

    const pCountry = document.createElement('p');
    pCountry.className = 'card-text mb-1';
    const flag = pickCountryFlag(recipe.categories);
    pCountry.innerHTML = `<strong>Country:</strong> ${flag ? `<span class="fi fi-${flag}"></span>` : '-'}`;

    const pDiff = document.createElement('p');
    pDiff.className = 'card-text mb-1';
    pDiff.innerHTML = `<strong>Difficulty:</strong> ${recipe.difficulty || '-'}`;

    const badges = document.createElement('div');
    badges.className = 'mt-2 d-flex flex-wrap';
    badges.appendChild(buildBadges(recipe.categories));

    body.append(h4, pCountry, pDiff, badges);
    card.append(img, body);
    a.appendChild(card);

    const item = document.createElement('div');
    item.className = 'mi-item';
    item.appendChild(a);

    return item;
  };

  const recipeMatches = (recipe, wanted) => {
    if (!wanted) return true;
    const cats = (recipe.categories || []).map(toKey);
    return cats.includes(wanted);
  };

  const getTrack = (section) => section.querySelector('.mi-track');
  const getPrevBtn = (section) => section.querySelector('.mi-prev');
  const getNextBtn = (section) => section.querySelector('.mi-next');
  const getViewport = (section) => section.querySelector('.mi-viewport');

  const enableControls = (section) => {
    const viewport = getViewport(section);
    const prev = getPrevBtn(section);
    const next = getNextBtn(section);
    const track = getTrack(section);

    if (!viewport || !track) return;

    let autoSlideInterval = null;
    let resumeTimeout = null;

    const stepPx = () => {
      if (!track.children.length) return 0;

      const firstItem = track.children[0];
      const itemWidth = firstItem.offsetWidth;
      const trackStyle = window.getComputedStyle(track);
      const gap = parseFloat(trackStyle.gap) || 0;

      return itemWidth + gap;
    };

    const maxScrollLeft = () => Math.max(0, track.scrollWidth - viewport.clientWidth);

    const nextSlide = () => {
      const step = stepPx();
      const currentScroll = viewport.scrollLeft;
      const maxScroll = maxScrollLeft();

      if (step <= 0) return;

      if (currentScroll >= maxScroll - 10) {
        viewport.scrollTo({ left: 0, behavior: 'smooth' });
      } else {
        viewport.scrollBy({ left: step, behavior: 'smooth' });
      }
    };

    const prevSlide = () => {
      const step = stepPx();
      const currentScroll = viewport.scrollLeft;
      const maxScroll = maxScrollLeft();

      if (step <= 0) return;

      if (currentScroll <= 10) {
        viewport.scrollTo({ left: maxScroll, behavior: 'smooth' });
      } else {
        viewport.scrollBy({ left: -step, behavior: 'smooth' });
      }
    };

    const stopAutoSlide = () => {
      clearInterval(autoSlideInterval);
      autoSlideInterval = null;
    };

    const startAutoSlide = () => {
      stopAutoSlide();
      if (track.children.length > 1) {
        autoSlideInterval = setInterval(nextSlide, 2000);
      }
    };

    const restartAutoSlideDelayed = (delay = 1500) => {
      clearTimeout(resumeTimeout);
      stopAutoSlide();
      resumeTimeout = setTimeout(startAutoSlide, delay);
    };

    prev?.addEventListener('click', () => {
      prevSlide();
      restartAutoSlideDelayed();
    });

    next?.addEventListener('click', () => {
      nextSlide();
      restartAutoSlideDelayed();
    });

    viewport.addEventListener('mouseenter', stopAutoSlide);
    viewport.addEventListener('mouseleave', startAutoSlide);

    viewport.addEventListener('touchstart', () => {
      restartAutoSlideDelayed(2500);
    }, { passive: true });

    viewport.addEventListener('touchend', () => {
      restartAutoSlideDelayed(2000);
    }, { passive: true });

    viewport.addEventListener('pointerdown', () => {
      restartAutoSlideDelayed(2500);
    });

    viewport.addEventListener('pointerup', () => {
      restartAutoSlideDelayed(2000);
    });

    viewport.addEventListener('scroll', () => {
      restartAutoSlideDelayed(2000);
    }, { passive: true });

    window.addEventListener('resize', () => {
      stopAutoSlide();
      clearTimeout(resumeTimeout);
      startAutoSlide();
    });

    startAutoSlide();
  };

  let recipes = [];
  try {
    const res = await fetch(RECIPES_JSON_URL, { cache: 'no-cache' });
    recipes = await res.json();
    if (!Array.isArray(recipes)) recipes = [];
  } catch (err) {
    console.error('Failed to load recipes.json:', err);
    return;
  }

  for (const section of sections) {
    const wanted = toKey(section.dataset.category || section.dataset.categorie || '');
    const track = getTrack(section);
    if (!track) continue;

    const list = recipes
      .filter(r => recipeMatches(r, wanted))
      .sort((a, b) => (a.title || '').localeCompare(b.title || '', 'de'));

    track.innerHTML = '';

    for (const r of list) {
      track.appendChild(buildCard(r));
    }

    if (!track.children.length) {
      const empty = document.createElement('div');
      empty.className = 'text-muted p-3 text-center';
      empty.textContent = 'No recipes found.';
      track.appendChild(empty);
    }

    enableControls(section);
  }
}