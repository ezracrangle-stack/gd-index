(function () {
  var input = document.getElementById('f'), list = document.getElementById('list');
  if (!input || !list) return;
  var rows = list.querySelectorAll('[data-q]');
  function norm(s) { return (s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase(); }
  rows.forEach(function (r) { r.dataset.n = norm(r.dataset.q); });
  var size = parseInt(list.dataset.per, 10) || 0;
  var render = size && window.gdPager ? window.gdPager(list, rows, size) : null;
  input.addEventListener('input', function () {
    var q = norm(input.value.trim());
    rows.forEach(function (r) {
      var ok = !q || r.dataset.n.indexOf(q) !== -1;
      r.dataset.m = ok ? '1' : '0';
      if (!render) r.hidden = !ok;
    });
    if (render) render(true);
  });
  if (render) render(false);
})();
