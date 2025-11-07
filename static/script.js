(function(){
  const html = document.documentElement;
  const toggle = document.getElementById('themeToggle');
  const menuBtn = document.getElementById('menuToggle');
  const nav = document.getElementById('nav');
  // theme
  const saved = localStorage.getItem('theme');
  if (saved) html.setAttribute('data-theme', saved);
  toggle?.addEventListener('click', ()=>{
    const next = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
  });
  // mobile menu
  menuBtn?.addEventListener('click', ()=>{
    if (nav.style.display === 'flex') { nav.style.display = 'none'; }
    else { nav.style.display = 'flex'; nav.style.flexDirection = 'column'; }
  });
})();

// Projects filter (client-side)
(function(){
  const grid = document.getElementById("projGrid");
  if (!grid) return;

  const btns = document.querySelectorAll(".filterbar .fbtn");
  btns.forEach(btn => {
    btn.addEventListener("click", () => {
      btns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      const filter = btn.getAttribute("data-filter");

      Array.from(grid.children).forEach(card => {
        const tags = (card.getAttribute("data-tags") || "").split(",").map(s => s.trim());
        const show = (filter === "*") || tags.includes(filter);
        card.style.display = show ? "" : "none";
      });
    });
  });
})();

// Shrink header / add shadow on scroll
window.addEventListener('scroll', () => {
  const header = document.querySelector('.site-header');
  if (window.scrollY > 20) header.classList.add('scrolled');
  else header.classList.remove('scrolled');
});
