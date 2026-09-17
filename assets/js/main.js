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

/* Background video: Chrome only honours muted autoplay when the property
   (not just the attribute) is set before play() is called. */
document.querySelectorAll('.sec__bg video').forEach(function (v) {
  v.muted = true;
  v.defaultMuted = true;
  var p = v.play();
  if (p && p.catch) p.catch(function () { /* autoplay refused; poster frame stands in */ });
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
