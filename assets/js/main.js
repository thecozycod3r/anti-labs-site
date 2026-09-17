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
   The sources are declared in the markup so the browser can judge autoplay
   eligibility while parsing. This only handles the cases where it still says no:
   the muted *property* (not just the attribute) has to be set, and Safari
   refuses outright under Low Power Mode or a per-site auto-play setting. So try
   at every point the state could change, and again on the first user gesture. */
document.querySelectorAll('video.bg-video, .sec__bg video').forEach(function (v) {
  v.muted = true;
  v.defaultMuted = true;
  v.playsInline = true;

  var settled = false;

  function tryPlay() {
    if (settled || !v.paused) return;
    var p = v.play();
    if (p && p.then) p.then(function () { settled = true; }).catch(function () {});
  }

  ['loadedmetadata', 'loadeddata', 'canplay', 'canplaythrough'].forEach(function (e) {
    v.addEventListener(e, tryPlay);
  });

  // any gesture is enough to satisfy a blocked autoplay policy
  ['pointerdown', 'touchstart', 'keydown', 'wheel', 'scroll', 'mousemove'].forEach(function (e) {
    window.addEventListener(e, tryPlay, { passive: true });
  });

  document.addEventListener('visibilitychange', function () {
    if (!document.hidden) tryPlay();
  });

  // start it once it is actually on screen, and pause when it is not
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) tryPlay();
        else if (!v.paused) v.pause();
      });
    }, { threshold: 0.1 }).observe(v);
  }

  tryPlay();
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
