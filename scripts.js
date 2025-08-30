// adding Navbar and Footer
document.addEventListener("DOMContentLoaded", () => {
const loadPartial = (id, url) => {
	const el = document.getElementById(id);
	if (el) {
	fetch(url)
		.then(r => r.text())
		.then(html => el.innerHTML = html)
		.catch(err => console.error(`Fehler beim Laden von ${url}:`, err));
	}
};

loadPartial("site-navbar", "navbar.html");
loadPartial("site-footer", "footer.html");
});


// Carousel
document.addEventListener('DOMContentLoaded', function () {
	let multipleCardCarousel = document.querySelector("#carouselExampleControls");

	if (window.matchMedia("(min-width: 768px)").matches) {
		let carousel = new bootstrap.Carousel(multipleCardCarousel, {
			interval: false,
			wrap: false
		});

		let carouselInner = document.querySelector("#carouselExampleControls .carousel-inner");
		let carouselWidth = carouselInner.scrollWidth;
		let cardWidth = document.querySelector(".carousel-item").offsetWidth;
		let scrollPosition = 0;

		// NEXT
		document.querySelector("#carouselExampleControls .carousel-control-next")
			.addEventListener("click", function () {
				if (scrollPosition < carouselWidth - cardWidth * 4) {
					scrollPosition += cardWidth;
					carouselInner.scroll({ left: scrollPosition, behavior: 'smooth' });
				} else {
					// am Ende -> zurück zum Anfang
					scrollPosition = 0;
					carouselInner.scroll({ left: scrollPosition, behavior: 'smooth' });
				}
			});

		// PREV
		document.querySelector("#carouselExampleControls .carousel-control-prev")
			.addEventListener("click", function () {
				if (scrollPosition > 0) {
					scrollPosition -= cardWidth;
					carouselInner.scroll({ left: scrollPosition, behavior: 'smooth' });
				} else {
					// am Anfang -> springe ans Ende
					scrollPosition = carouselWidth - cardWidth * 4;
					carouselInner.scroll({ left: scrollPosition, behavior: 'smooth' });
				}
			});
	} else {
		multipleCardCarousel.classList.add("slide");
	}
});



// Carousel
(function () {
	const track = document.getElementById('miTrack');
	const btnNext = document.getElementById('btnNext');
	const btnPrev = document.getElementById('btnPrev');

	let animating = false;

	const getStep = () => {
		const first = track.children[0];
		const rect = first.getBoundingClientRect();
		let gap = 0;
		if (track.children.length > 1) {
		const second = track.children[1];
		gap = second.getBoundingClientRect().left - rect.right;
		}
		return rect.width + gap;
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
		animating = true;
		const step = getStep();
		animateTo(-step, () => {
		track.appendChild(track.firstElementChild);
		});
	};

	const prev = () => {
		if (animating) return;
		animating = true;
		const step = getStep();
		track.style.transition = 'none';
		track.insertBefore(track.lastElementChild, track.firstElementChild);
		track.style.transform = `translateX(${-step}px)`;
		requestAnimationFrame(() => {
		requestAnimationFrame(() => {
			animateTo(0);
		});
		});
	};

	btnNext.addEventListener('click', next);
	btnPrev.addEventListener('click', prev);

	// Auto-Slide alle 2.5s
	const AUTOPLAY_MS = 2500;
	setInterval(() => {
	if (!animating) next();
	}, AUTOPLAY_MS);


	// Optional: Swipe-Unterstützung für Touch
	let startX = 0;
	track.addEventListener('pointerdown', (e) => { startX = e.clientX; });
	track.addEventListener('pointerup', (e) => {
		const dx = e.clientX - startX;
		if (Math.abs(dx) > 30) {
		dx < 0 ? next() : prev();
		}
	});

	window.addEventListener('resize', () => {
		track.style.transition = 'none';
		track.style.transform = 'translateX(0px)';
	});
	})();