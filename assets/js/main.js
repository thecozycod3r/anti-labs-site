/* Accordions — one open at a time within a list, matching the source. */
document.querySelectorAll('.acc').forEach(function (list) {
  list.querySelectorAll('.acc__btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var item = btn.closest('.acc__item');
      var willOpen = !item.classList.contains('is-open');

      list.querySelectorAll('.acc__item').forEach(function (other) {
        other.classList.remove('is-open');
        var b = other.querySelector('.acc__btn');
        if (b) b.setAttribute('aria-expanded', 'false');
      });

      if (willOpen) {
        item.classList.add('is-open');
        btn.setAttribute('aria-expanded', 'true');
      }
    });
  });
});

/* Header retracts while scrolling down, returns on scroll up — as the source does. */
(function () {
  var header = document.querySelector('.masthead');
  if (!header) return;
  var last = window.scrollY;
  var ticking = false;

  function update() {
    var y = window.scrollY;
    var height = header.offsetHeight;
    if (y > height && y > last) {
      header.classList.add('is-hidden');
    } else if (y < last) {
      header.classList.remove('is-hidden');
    }
    last = y;
    ticking = false;
  }

  window.addEventListener('scroll', function () {
    if (!ticking) {
      ticking = true;
      window.requestAnimationFrame(update);
    }
  }, { passive: true });
})();

/* Background video.
   Two things bite here. Browsers only honour muted autoplay when the *property*
   is set (not just the attribute), and Safari still refuses when Low Power Mode
   is on or the site's auto-play setting says no — in which case it paints its
   own play button over the poster. So: pick a source sized for the viewport,
   set muted properly, then retry on the first user gesture if it was refused. */
document.querySelectorAll('video.bg-video, .sec__bg video').forEach(function (v) {
  var mobile = window.matchMedia('(max-width: 767px)').matches;
  var src = v.getAttribute(mobile ? 'data-src-mobile' : 'data-src-desktop');
  if (src && !v.getAttribute('src')) v.setAttribute('src', src);

  v.muted = true;
  v.defaultMuted = true;
  v.playsInline = true;
  v.setAttribute('muted', '');

  function attempt() {
    var p = v.play();
    if (p && p.catch) {
      p.catch(function () {
        // refused — wait for any gesture, then try once more
        ['pointerdown', 'touchstart', 'keydown', 'scroll'].forEach(function (evt) {
          window.addEventListener(evt, retry, { once: true, passive: true });
        });
      });
    }
  }

  function retry() {
    var p = v.play();
    if (p && p.catch) p.catch(function () { /* poster frame stands in */ });
  }

  if (v.readyState >= 2) attempt();
  else v.addEventListener('loadeddata', attempt, { once: true });

  // a backgrounded tab pauses it; resume when the page is visible again
  document.addEventListener('visibilitychange', function () {
    if (!document.hidden && v.paused) retry();
  });
});

/* Contact form: no backend here, so acknowledge in place. */
var contactForm = document.querySelector('.s-contact__form');
if (contactForm) {
  contactForm.addEventListener('submit', function (e) {
    e.preventDefault();
    var btn = contactForm.querySelector('button[type="submit"]');
    if (!btn) return;
    var original = btn.textContent;
    btn.textContent = 'Thanks — we’ll be in touch';
    setTimeout(function () { btn.textContent = original; }, 2600);
  });
}
