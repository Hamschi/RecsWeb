document.addEventListener("DOMContentLoaded", () => {
  const input = document.getElementById("suche");
  const karten = Array.from(document.querySelectorAll(".karte"));
  if (!input) return;

  input.addEventListener("input", () => {
    const q = input.value.trim().toLowerCase();
    karten.forEach((k) => {
      const text = k.textContent.toLowerCase();
      k.style.display = text.includes(q) ? "" : "none";
    });
  });
});
