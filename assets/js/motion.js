/* ==========================================================================
   Motion layer. Progressive: with JS off, or reduced motion on, every element
   is left in its resting state.
   ========================================================================== */
(function () {
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var raf = window.requestAnimationFrame.bind(window);

  /* ---- 1. split [data-split] headings into masked lines ----------------- */
  document.querySelectorAll('[data-split]').forEach(function (el) {
    var mode = el.getAttribute('data-split');
    var parts = el.innerHTML.split(/<br\s*\/?>/i);

    if (mode === 'chars') {
      var c = 0;
      el.innerHTML = parts.map(function (part) {
        // split to text nodes only, so markup like <em> keeps working
        var tmp = document.createElement('div');
        tmp.innerHTML = part;
        var out = '';
        [].forEach.call(tmp.childNodes, function (node) {
          var text = node.textContent;
          var open = '', close = '';
          if (node.nodeType === 1) {
            open = '<' + node.tagName.toLowerCase() + '>';
            close = '</' + node.tagName.toLowerCase() + '>';
          }
          out += open + text.split('').map(function (ch) {
            if (ch === ' ') return '<span class="char">&nbsp;</span>';
            return '<span class="char"><span class="char__inner" style="--c:' + (c++) + '">' +
                   ch + '</span></span>';
          }).join('') + close;
        });
        return '<span class="line">' + out + '</span>';
      }).join('<br>');
      return;
    }

    if (mode !== 'words') {
      el.innerHTML = parts.map(function (part, i) {
        return '<span class="line"><span class="line__inner" style="--i:' + i + '">' + part + '</span></span>';
      }).join('');
      return;
    }

    /* Word mode: each word masks independently. Split on whitespace that sits
       outside a tag so markup like <em>Motion</em> survives intact. */
    var w = 0;
    el.innerHTML = parts.map(function (part) {
      var words = part.trim().split(/\s+(?![^<]*>)/);
      return '<span class="line">' + words.map(function (word) {
        return '<span class="word"><span class="word__inner" style="--w:' + (w++) + '">' +
               word + '</span></span>';
      }).join(' ') + '</span>';
    }).join('<br>');
  });

  /* ---- 2. observe everything that animates in --------------------------- */
  var targets = document.querySelectorAll('.reveal, .reveal-img, .hero-plate, .hero-rule, [data-split]');
  var pending = [];
  var sweep = null;

  if (reduce || !('IntersectionObserver' in window)) {
    targets.forEach(function (el) { el.classList.add('is-in'); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        e.target.classList.add('is-in');
        if (e.target.classList.contains('chroma')) focus(e.target);
        io.unobserve(e.target);
      });
    }, { rootMargin: '0px 0px -10% 0px', threshold: 0.04 });

    targets.forEach(function (el) {
      // anything already on screen at load animates immediately
      var r = el.getBoundingClientRect();
      if (r.top < window.innerHeight * 0.92 && r.bottom > 0) {
        raf(function () { el.classList.add('is-in'); });
      } else {
        io.observe(el);
      }
    });

    /* Safety net. IntersectionObserver delivers asynchronously and can miss
       entries during fast or programmatic scrolling, which would strand an
       element in its hidden state. This sweep is cheap and deterministic. */
    pending = [].slice.call(targets);
    sweep = function () {
      if (!pending.length) return;
      var vh = window.innerHeight;
      pending = pending.filter(function (el) {
        if (el.classList.contains('is-in')) return false;
        var r = el.getBoundingClientRect();
        if (r.top < vh * 0.92 && r.bottom > 0) {
          el.classList.add('is-in');
          io.unobserve(el);
          return false;
        }
        return true;
      });
    };
  }

  /* ---- 3. nav label swap ------------------------------------------------ */
  document.querySelectorAll('.nav__link').forEach(function (a) {
    var text = a.textContent.trim();
    a.innerHTML = '<span class="swap" data-label="' + text + '">' + text + '</span>';
  });

  /* ---- 4. scroll progress + parallax ------------------------------------ */
  var bar = document.createElement('div');
  bar.className = 'progress';
  document.body.appendChild(bar);

  var parallax = [].slice.call(document.querySelectorAll('[data-parallax]'));
  var floaters = [].slice.call(document.querySelectorAll('[data-float]'));
  var chroma = [].slice.call(document.querySelectorAll('.chroma'));

  /* Parallax and the idle float both want `transform`, so nothing writes it
     directly — they set their own channel and this composes the result. */
  /* ease --cx to 0 so the ghosts slide together as the letters land */
  function focus(el) {
    if (reduce) { el.style.setProperty('--cx', '0px'); return; }
    var from = 14, start = null, dur = 1100;
    (function step(t) {
      if (start === null) start = t;
      var k = Math.min(1, (t - start) / dur);
      var eased = 1 - Math.pow(1 - k, 3);
      el.style.setProperty('--cx', (from * (1 - eased)).toFixed(2) + 'px');
      if (k < 1) raf(step);
    })(performance.now());
  }

  function write(el) {
    var y = (el._px || 0) + (el._fy || 0);
    el.style.transform = 'translate3d(0,' + y.toFixed(2) + 'px,0)';
  }

  /* Idle float: a slow, low-amplitude drift so the collage is alive before
     the visitor scrolls. Each plate gets its own phase and period. */
  if (!reduce && floaters.length) {
    floaters.forEach(function (el, i) {
      el._amp = parseFloat(el.getAttribute('data-float')) || 5;
      el._period = 6200 + i * 900;
      el._phase = i * 1.7;
    });
    (function floatLoop(t) {
      var vh = window.innerHeight;
      for (var i = 0; i < floaters.length; i++) {
        var el = floaters[i];
        var r = el.getBoundingClientRect();
        if (r.bottom < 0 || r.top > vh) continue;           // off screen: skip the write
        el._fy = Math.sin((t / el._period) * Math.PI * 2 + el._phase) * el._amp;
        write(el);
      }
      raf(floatLoop);
    })(0);
  }

  var ticking = false;

  function onScroll() {
    var doc = document.documentElement;
    var max = doc.scrollHeight - window.innerHeight;
    var pct = max > 0 ? window.scrollY / max : 0;
    bar.style.transform = 'scaleX(' + pct.toFixed(4) + ')';

    if (!reduce) {
      var vh = window.innerHeight;
      parallax.forEach(function (el) {
        var r = el.getBoundingClientRect();
        if (r.bottom < -200 || r.top > vh + 200) return;
        var amount = parseFloat(el.getAttribute('data-parallax')) || 0.08;
        var centre = r.top + r.height / 2 - vh / 2;
        el._px = Math.max(-110, Math.min(110, -centre * amount));
        write(el);
      });
    }
    /* chromatic focus: converged while the hero is at rest, separating as it
       scrolls away — like a lens pulling out of focus */
    if (!reduce && chroma.length) {
      var prog = Math.min(1, Math.max(0, window.scrollY / (window.innerHeight * 0.85)));
      chroma.forEach(function (el) {
        if (!el.classList.contains('is-in')) return;
        el.style.setProperty('--cx', (prog * 18).toFixed(1) + 'px');
      });
    }

    if (sweep) sweep();
    ticking = false;
  }

  window.addEventListener('scroll', function () {
    if (!ticking) { ticking = true; raf(onScroll); }
  }, { passive: true });
  onScroll();

  /* ---- 5. cursor spotlight over hero imagery ---------------------------- */
  if (!reduce && window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
    document.querySelectorAll('.p-hero, .sec__bg--spot').forEach(function (zone) {
      var surface = zone.classList.contains('p-hero')
        ? zone.querySelector('.p-hero__bg')
        : zone;
      if (!surface) return;
      zone.addEventListener('pointermove', function (e) {
        var r = surface.getBoundingClientRect();
        surface.style.setProperty('--mx', ((e.clientX - r.left) / r.width * 100).toFixed(2) + '%');
        surface.style.setProperty('--my', ((e.clientY - r.top) / r.height * 100).toFixed(2) + '%');
        surface.classList.add('is-lit');
      });
      zone.addEventListener('pointerleave', function () {
        surface.classList.remove('is-lit');
      });
    });
  }

  /* ---- 7. viewfinder reticle cursor ------------------------------------- */
  if (!reduce && window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
    var cur = document.createElement('div');
    cur.className = 'cursor';
    cur.setAttribute('aria-hidden', 'true');
    cur.innerHTML =
      '<span class="cursor__box">' +
        '<span class="cursor__c cursor__c--tl"></span>' +
        '<span class="cursor__c cursor__c--tr"></span>' +
        '<span class="cursor__c cursor__c--bl"></span>' +
        '<span class="cursor__c cursor__c--br"></span>' +
      '</span>' +
      '<span class="cursor__dot"></span>' +
      '<span class="cursor__label"></span>';
    document.body.appendChild(cur);
    document.body.classList.add('has-reticle');

    var box = cur.querySelector('.cursor__box');
    var dot = cur.querySelector('.cursor__dot');
    var label = cur.querySelector('.cursor__label');

    var tx = innerWidth / 2, ty = innerHeight / 2;   // target (pointer)
    var bx = tx, by = ty;                            // brackets, eased behind

    var LOCK = 'a, button, .p-strip__cell, .acc__btn, input, textarea, select, [data-cursor]';

    document.addEventListener('pointermove', function (e) {
      tx = e.clientX; ty = e.clientY;
      cur.classList.add('is-active');

      var hit = e.target.closest ? e.target.closest(LOCK) : null;
      if (hit) {
        var typing = /^(INPUT|TEXTAREA|SELECT)$/.test(hit.tagName);
        cur.classList.toggle('is-text', typing);
        cur.classList.toggle('is-locked', !typing);
        if (!typing) {
          label.textContent = hit.getAttribute('data-cursor') ||
            (hit.tagName === 'A' ? 'Open' : hit.classList.contains('acc__btn') ? 'Expand' : 'View');
        }
      } else {
        cur.classList.remove('is-locked', 'is-text');
        label.textContent = '';
      }
    }, { passive: true });

    document.addEventListener('pointerdown', function () { cur.classList.add('is-down'); });
    document.addEventListener('pointerup',   function () { cur.classList.remove('is-down'); });
    document.addEventListener('pointerleave', function () { cur.classList.remove('is-active'); });

    (function ride() {
      bx += (tx - bx) * 0.18;                        // brackets lag, dot is exact
      by += (ty - by) * 0.18;
      box.style.transform = 'translate3d(' + bx.toFixed(1) + 'px,' + by.toFixed(1) + 'px,0)';
      label.style.transform = 'translate3d(' + bx.toFixed(1) + 'px,' + by.toFixed(1) + 'px,0)';
      dot.style.transform = 'translate3d(' + tx + 'px,' + ty + 'px,0)';
      raf(ride);
    })();
  }

  /* ---- 6. page transition wipe ------------------------------------------ */
  if (!reduce) {
    var wipe = document.createElement('div');
    wipe.className = 'wipe';
    document.body.appendChild(wipe);

    document.body.classList.add('is-entering');
    setTimeout(function () { document.body.classList.remove('is-entering'); }, 700);

    document.addEventListener('click', function (e) {
      var a = e.target.closest('a');
      if (!a) return;
      var href = a.getAttribute('href');
      if (!href || href.charAt(0) === '#' || a.target === '_blank') return;
      if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button !== 0) return;
      if (a.hostname && a.hostname !== window.location.hostname) return;
      if (!/\.html?$/.test(href)) return;

      e.preventDefault();
      document.body.classList.add('is-leaving');
      setTimeout(function () { window.location.href = href; }, 430);
    });

    // restore on back/forward out of the bfcache
    window.addEventListener('pageshow', function (ev) {
      if (ev.persisted) document.body.classList.remove('is-leaving');
    });
  }
})();
