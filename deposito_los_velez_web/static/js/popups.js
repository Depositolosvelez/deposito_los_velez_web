(function () {
  // ===== TOP BAR =====
  var tb = document.getElementById('top-bar');
  if (tb && localStorage.getItem('topbar_cerrada')) tb.style.display = 'none';
  window.cerrarTopBar = function () {
    if (tb) tb.style.display = 'none';
    localStorage.setItem('topbar_cerrada', '1');
  };

  // ===== POPUP ENTRADA — aparece a los 35 segundos, una sola vez por navegador =====
  var entEl = document.getElementById('popup-entrada');
  if (entEl && !localStorage.getItem('popup_entrada_ok')) {
    setTimeout(function () {
      entEl.style.display = 'flex';
      localStorage.setItem('popup_entrada_ok', '1');
    }, 35000);
    var entForm = entEl.querySelector('form');
    if (entForm) {
      entForm.addEventListener('submit', function () {
        localStorage.setItem('popup_entrada_ok', '1');
      });
    }
  }
  window.cerrarPopupEntrada = function () {
    if (entEl) entEl.style.display = 'none';
    localStorage.setItem('popup_entrada_ok', '1');
  };

  // ===== POPUP SALIDA — exit intent, una vez por sesión, solo desktop =====
  var salEl = document.getElementById('popup-salida');
  document.addEventListener('mouseleave', function (e) {
    if (e.clientY < 5 && salEl && !sessionStorage.getItem('popup_salida_ok')) {
      salEl.style.display = 'flex';
      sessionStorage.setItem('popup_salida_ok', '1');
    }
  });
  window.cerrarPopupSalida = function () {
    if (salEl) salEl.style.display = 'none';
  };

  // ===== CERRAR POPUPS AL CLIC EN EL OVERLAY =====
  document.addEventListener('click', function (e) {
    [entEl, salEl].forEach(function (el) {
      if (el && e.target === el) el.style.display = 'none';
    });
  });

  // ===== ANIMACIONES DE TARJETAS =====
  document.addEventListener('DOMContentLoaded', function () {
    var cards = document.querySelectorAll('.card-animate');
    cards.forEach(function (card, index) {
      card.style.animationDelay = (index * 0.15) + 's';
      card.classList.add('fade-in-up');
    });
  });
})();
