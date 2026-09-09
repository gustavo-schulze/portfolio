/* Gustavo Gorges - Soluções em Dados & Tecnologia
   Sem dependências. Menu mobile, revelação ao rolar e ano do rodapé. */

(function () {
  'use strict';

  // ---------- ano do rodapé ----------
  var ano = document.getElementById('ano');
  if (ano) ano.textContent = new Date().getFullYear();

  // ---------- menu mobile ----------
  var toggle = document.getElementById('navToggle');
  var links = document.getElementById('navLinks');

  function fecharMenu() {
    if (!links) return;
    links.classList.remove('open');
    if (toggle) toggle.setAttribute('aria-expanded', 'false');
  }

  if (toggle && links) {
    toggle.addEventListener('click', function () {
      var aberto = links.classList.toggle('open');
      toggle.setAttribute('aria-expanded', String(aberto));
    });

    // fecha ao escolher um destino
    links.addEventListener('click', function (e) {
      if (e.target.tagName === 'A') fecharMenu();
    });

    // fecha ao clicar fora ou apertar Esc
    document.addEventListener('click', function (e) {
      if (!links.contains(e.target) && !toggle.contains(e.target)) fecharMenu();
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') fecharMenu();
    });
    // ao voltar para desktop, o menu não pode ficar preso aberto
    window.addEventListener('resize', function () {
      if (window.innerWidth > 720) fecharMenu();
    });
  }

  // ---------- revelação ao rolar ----------
  var alvos = document.querySelectorAll('.rv');

  // Sem IntersectionObserver ou com movimento reduzido: mostra tudo de uma vez.
  var reduzido = window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (!('IntersectionObserver' in window) || reduzido) {
    for (var i = 0; i < alvos.length; i++) alvos[i].classList.add('in');
    return;
  }

  var obs = new IntersectionObserver(function (entradas) {
    entradas.forEach(function (entrada) {
      if (!entrada.isIntersecting) return;
      entrada.target.classList.add('in');
      obs.unobserve(entrada.target);          // anima uma vez só
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -60px 0px' });

  alvos.forEach(function (el, i) {
    el.style.transitionDelay = Math.min(i % 5, 4) * 60 + 'ms';
    obs.observe(el);
  });
})();
