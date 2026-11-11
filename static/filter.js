(function () {
  var input = document.getElementById('f'), list = document.getElementById('list');
  if (!input || !list) return;
  var rows = list.querySelectorAll('[data-q]');
  function norm(s) { return (s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase(); }
  rows.forEach(function (r) { r.dataset.n = norm(r.dataset.q); });
  input.addEventListener('input', function () {
    var q = norm(input.value.trim());
    rows.forEach(function (r) { r.hidden = q && r.dataset.n.indexOf(q) === -1; });
  });
})();
