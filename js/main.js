/**
 * main.js — Empire Ottoman · Balkans 1354–1683
 * Interactions : hover timeline sultans + animations au scroll
 */

// ─── 1. TOOLTIP SULTANS (index.html) ─────────────────────────────────────────

function initSultanTooltips() {
  const segments = document.querySelectorAll(".tb-seg");
  if (!segments.length) return;

  // Créer le tooltip
  const tooltip = document.createElement("div");
  tooltip.className = "sultan-tooltip";
  document.body.appendChild(tooltip);

  const sultansInfo = {
    "Orhan"        : { dates: "1326–1362", batailles: 6,  info: "Premières incursions en Thrace" },
    "Murad Iᵉʳ"   : { dates: "1362–1389", batailles: 8,  info: "Conquête d'Edirne et de la Bulgarie" },
    "Bayezid Iᵉʳ" : { dates: "1389–1402", batailles: 5,  info: "Siège de Constantinople, défaite à Ankara" },
    "Interrègne"   : { dates: "1402–1413", batailles: 2,  info: "Guerre civile entre fils de Bayezid" },
    "Mehmed Iᵉʳ"  : { dates: "1413–1421", batailles: 6,  info: "Réunification de l'Empire" },
    "Murad II"     : { dates: "1421–1451", batailles: 20, info: "Consolidation dans les Balkans" },
    "Mehmed II"    : { dates: "1451–1481", batailles: 34, info: "Prise de Constantinople (1453)" },
    "Bayezid II"   : { dates: "1481–1512", batailles: 15, info: "Expansion en mer Égée et Adriatique" },
    "Selim Iᵉʳ"   : { dates: "1512–1520", batailles: 3,  info: "Conquêtes en Orient plutôt qu'en Europe" },
    "Soliman Iᵉʳ" : { dates: "1520–1566", batailles: 22, info: "Apogée de l'Empire, siège de Vienne (1529)" },
    "Selim II"     : { dates: "1566–1574", batailles: 6,  info: "Conquête de Chypre" },
    "Murad III"    : { dates: "1574–1595", batailles: 8,  info: "Guerres austro-ottomanes" },
    "Mehmed III"   : { dates: "1595–1603", batailles: 20, info: "Longue guerre contre les Habsbourg" },
    "Ahmed Iᵉʳ"   : { dates: "1603–1617", batailles: 3,  info: "Campagnes surtout sur le front perse" },
    "Mustafa Iᵉʳ" : { dates: "1617–1618", batailles: 1,  info: "Règne très court, peu d'activité balkanique" },
    "Osman II"     : { dates: "1618–1622", batailles: 2,  info: "Défaite de Khotin contre la Pologne" },
    "Murad IV"     : { dates: "1623–1640", batailles: 5,  info: "Priorité au front oriental contre la Perse" },
    "Ibrahim Iᵉʳ" : { dates: "1640–1648", batailles: 7,  info: "Guerre de Crète, début du conflit vénitien" },
    "Mehmed IV"    : { dates: "1648–1683", batailles: 25, info: "Second siège de Vienne, début du recul" },
  };

  segments.forEach(seg => {
    const title = seg.getAttribute("title") || "";
    // Extraire le nom du sultan depuis le title "Nom (dates)"
    const sultanName = title.split(" (")[0];
    const info = sultansInfo[sultanName];

    seg.addEventListener("mouseenter", (e) => {
      if (!info) return;
      tooltip.innerHTML = `
        <div class="tt-name">${sultanName}</div>
        <div class="tt-dates">${info.dates}</div>
        <div class="tt-battles"><span>${info.batailles}</span> batailles</div>
        <div class="tt-info">${info.info}</div>
      `;
      tooltip.classList.add("visible");
      positionTooltip(e);
    });

    seg.addEventListener("mousemove", positionTooltip);

    seg.addEventListener("mouseleave", () => {
      tooltip.classList.remove("visible");
    });
  });

  function positionTooltip(e) {
    const x = e.clientX + 14;
    const y = e.clientY - 10;
    const tw = tooltip.offsetWidth;
    const th = tooltip.offsetHeight;
    const vw = window.innerWidth;
    const vh = window.innerHeight;

    tooltip.style.left = (x + tw > vw ? x - tw - 28 : x) + "px";
    tooltip.style.top  = (y + th > vh ? y - th : y) + "px";
  }
}

// ─── 2. ANIMATIONS AU SCROLL ──────────────────────────────────────────────────

function initScrollAnimations() {
  const targets = document.querySelectorAll(
    ".card, .content-section, .hero-stats, .timeline-preview, " +
    ".viz-block, .analysis-interp, .report-grid, .step-header, .method-note"
  );

  if (!targets.length) return;

  // Appliquer l'état initial invisible
  targets.forEach(el => el.classList.add("anim-hidden"));

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.remove("anim-hidden");
        entry.target.classList.add("anim-visible");
        observer.unobserve(entry.target);
      }
    });
  }, {
    threshold: 0.1,
    rootMargin: "0px 0px -40px 0px"
  });

  targets.forEach(el => observer.observe(el));
}

// ─── 3. HIGHLIGHT ACTIF NAV ───────────────────────────────────────────────────

function initNavHighlight() {
  const links = document.querySelectorAll(".nav-links a");
  const current = window.location.pathname.split("/").pop() || "index.html";
  links.forEach(link => {
    const href = link.getAttribute("href");
    if (href === current) link.classList.add("active");
  });
}

// ─── INIT ─────────────────────────────────────────────────────────────────────

document.addEventListener("DOMContentLoaded", () => {
  initSultanTooltips();
  initScrollAnimations();
  initNavHighlight();
});