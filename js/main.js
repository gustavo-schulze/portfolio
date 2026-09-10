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

  // ---------- aria-current no item do menu correspondente à seção visível ----------
  var navAncoras = links ? links.querySelectorAll('a[href^="#"]') : [];
  var secoes = [];
  navAncoras.forEach(function (a) {
    var alvo = document.getElementById(a.getAttribute('href').slice(1));
    if (alvo) secoes.push({ link: a, el: alvo });
  });

  if (secoes.length && 'IntersectionObserver' in window) {
    var navObs = new IntersectionObserver(function (entradas) {
      entradas.forEach(function (entrada) {
        var item = secoes.filter(function (s) { return s.el === entrada.target; })[0];
        if (!item) return;
        if (entrada.isIntersecting) {
          secoes.forEach(function (s) { s.link.removeAttribute('aria-current'); });
          item.link.setAttribute('aria-current', 'true');
        }
      });
    }, { rootMargin: '-45% 0px -50% 0px', threshold: 0 });
    secoes.forEach(function (s) { navObs.observe(s.el); });
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
