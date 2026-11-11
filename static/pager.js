// Splits a long list into pages. Rows a filter has ruled out carry data-m="0".
// Without JavaScript the full list shows.
window.gdPager = function (list, rows, size) {
  rows = Array.prototype.slice.call(rows);
  var nav = document.createElement('nav');
  nav.className = 'pager';
  nav.setAttribute('aria-label', 'Pages');
  list.parentNode.insertBefore(nav, list.nextSibling);
  var page = parseInt(new URLSearchParams(location.search).get('page'), 10) || 1;

  function btn(label, target, opts) {
    var b = document.createElement('button');
    b.type = 'button';
    b.textContent = label;
    if (opts && opts.current) b.setAttribute('aria-current', 'page');
    if (opts && opts.disabled) b.disabled = true;
    if (opts && opts.aria) b.setAttribute('aria-label', opts.aria);
    b.addEventListener('click', function () {
      page = target;
      render(false);
      var top = list.getBoundingClientRect().top + window.pageYOffset - 90;
      if (window.pageYOffset > top) window.scrollTo(0, top);
    });
    return b;
  }

  function gap() {
    var s = document.createElement('span');
    s.className = 'gap';
    s.textContent = '…';
    return s;
  }

  function render(reset) {
    if (reset) page = 1;
    var shown = rows.filter(function (r) { return r.dataset.m !== '0'; });
    var pages = Math.max(1, Math.ceil(shown.length / size));
    if (page > pages) page = pages;
    if (page < 1) page = 1;
    var from = (page - 1) * size;
    rows.forEach(function (r) { r.hidden = true; });
    shown.slice(from, from + size).forEach(function (r) { r.hidden = false; });

    nav.innerHTML = '';
    nav.hidden = pages < 2;
    if (pages > 1) {
      nav.appendChild(btn('← Prev', page - 1, { disabled: page === 1, aria: 'Previous page' }));
      var last = 0;
      for (var i = 1; i <= pages; i++) {
        if (i === 1 || i === pages || Math.abs(i - page) <= 1) {
          if (last && i - last > 1) nav.appendChild(gap());
          nav.appendChild(btn(String(i), i, { current: i === page, aria: 'Page ' + i }));
          last = i;
        }
      }
      nav.appendChild(btn('Next →', page + 1, { disabled: page === pages, aria: 'Next page' }));
      var info = document.createElement('span');
      info.className = 'small pinfo';
      info.textContent = (from + 1) + '–' + Math.min(from + size, shown.length) + ' of ' + shown.length;
      nav.appendChild(info);
    }

    var q = new URLSearchParams(location.search);
    if (page > 1) q.set('page', page); else q.delete('page');
    if (history.replaceState) history.replaceState(null, '', q.toString() ? '?' + q : location.pathname);
  }

  return render;
};
