(function () {
  var box = document.getElementById('results'), input = document.getElementById('q');
  if (!box || !input) return;
  var root = box.dataset.root, data = null;
  var ORDER = ['Investors', 'Companies', 'Student pitches', 'Topics'];
  function norm(s) { return (s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase(); }
  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text) e.textContent = text; return e; }
  function run() {
    var raw = input.value.trim(), q = norm(raw);
    box.innerHTML = '';
    if (history.replaceState) history.replaceState(null, '', q ? '?q=' + encodeURIComponent(raw) : location.pathname);
    if (!q || !data) return;
    var words = q.split(/\s+/), found = 0;
    ORDER.forEach(function (kind) {
      var hits = data.filter(function (d) {
        if (d.k !== kind) return false;
        var s = norm(d.n + ' ' + d.m + ' ' + d.x);
        return words.every(function (w) { return s.indexOf(w) !== -1; });
      }).slice(0, 40);
      if (!hits.length) return;
      found += hits.length;
      box.appendChild(el('p', 'cta-kicker', kind));
      var ul = el('ul', 'sresults');
      hits.forEach(function (d) {
        var li = el('li'), a = el('a', null, d.n); a.href = root + d.u; li.appendChild(a);
        if (d.m) li.appendChild(el('span', 'smeta', d.m));
        ul.appendChild(li);
      });
      box.appendChild(ul);
    });
    if (!found) box.appendChild(el('p', 'small', 'Nothing found. Try a last name, a firm or part of a company name.'));
  }
  fetch(box.dataset.index).then(function (r) { return r.json(); }).then(function (d) {
    data = d;
    var p = new URLSearchParams(location.search).get('q');
    if (p) input.value = p;
    run();
  });
  input.addEventListener('input', run);
})();
