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
