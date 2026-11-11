(function () {
  var box = document.getElementById('pfilters');
  if (!box) return;
  box.hidden = false;                       // without JavaScript the full table shows
  var rows = document.querySelectorAll('.ptable tbody tr');
  var buttons = box.querySelectorAll('button[data-dir]');
  var year = document.getElementById('year'), count = document.getElementById('pcount');
  var dir = '';
  var p = new URLSearchParams(location.search);
  if (p.get('dir')) dir = p.get('dir');
  if (p.get('year')) year.value = p.get('year');
  function run() {
    var n = 0;
    rows.forEach(function (r) {
      var ok = (!dir || r.dataset.dir === dir) && (!year.value || r.dataset.year === year.value);
      r.hidden = !ok; if (ok) n++;
    });
    buttons.forEach(function (b) { b.setAttribute('aria-pressed', b.dataset.dir === dir ? 'true' : 'false'); });
    count.textContent = n + (n === 1 ? ' pitch' : ' pitches');
    var q = new URLSearchParams();
    if (dir) q.set('dir', dir);
    if (year.value) q.set('year', year.value);
    if (history.replaceState) history.replaceState(null, '', q.toString() ? '?' + q : location.pathname);
  }
  buttons.forEach(function (b) { b.addEventListener('click', function () { dir = b.dataset.dir; run(); }); });
  year.addEventListener('change', run);
  run();
})();
