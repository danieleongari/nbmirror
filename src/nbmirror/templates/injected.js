(function () {
  function ensureThemeToggle() {
    if (document.querySelector('.nbm-theme-toggle')) {
      return;
    }

    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'nbm-theme-toggle';
    btn.textContent = '🌙';
    btn.setAttribute('aria-label', 'Toggle dark mode');
    btn.setAttribute('aria-pressed', 'false');

    btn.addEventListener('click', function () {
      var dark = document.body.classList.toggle('nbm-dark');
      btn.textContent = dark ? '☀️' : '🌙';
      btn.setAttribute('aria-pressed', dark ? 'true' : 'false');
    });

    document.body.appendChild(btn);
  }

  function hasRenderedOutput(cell) {
    return Boolean(cell.querySelector('.output_subarea, .jp-OutputArea-child'));
  }

  function ensureGlobalControlsToggle() {
    if (document.querySelector('.nbm-controls-toggle')) {
      return;
    }

    var wrap = document.createElement('div');
    wrap.className = 'nbm-controls-wrap';

    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'nbm-controls-toggle';
    btn.textContent = 'Hide cell controls';
    btn.setAttribute('aria-pressed', 'false');

    btn.addEventListener('click', function () {
      var hidden = document.body.classList.toggle('nbm-controls-hidden');
      btn.textContent = hidden ? 'Show cell controls' : 'Hide cell controls';
      btn.setAttribute('aria-pressed', hidden ? 'true' : 'false');
    });

    wrap.appendChild(btn);

    var firstHome = document.querySelector('.nbm-home-wrap.nbm-home-top');
    if (firstHome && firstHome.parentNode) {
      firstHome.appendChild(wrap);
      return;
    }

    if (document.body.firstChild) {
      document.body.insertBefore(wrap, document.body.firstChild);
    } else {
      document.body.appendChild(wrap);
    }
  }

  function findCellInput(cell) {
    return cell.querySelector('.input, .jp-InputArea');
  }

  function ensureToggle(cell, idx) {
    if (cell.querySelector('.nbm-toggle')) {
      return;
    }

    var input = findCellInput(cell);
    if (!input) {
      return;
    }

    if (!hasRenderedOutput(cell)) {
      cell.classList.add('nbm-no-output');
    }

    cell.classList.remove('nbm-expanded');

    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'nbm-toggle';
    btn.textContent = 'Show code [' + (idx + 1) + ']';
    btn.setAttribute('aria-expanded', 'false');
    btn.setAttribute('aria-label', 'Toggle code for cell ' + (idx + 1));

    function setExpanded(expanded) {
      btn.textContent = expanded
        ? 'Hide code [' + (idx + 1) + ']'
        : 'Show code [' + (idx + 1) + ']';
      btn.setAttribute('aria-expanded', expanded ? 'true' : 'false');
      outNum.setAttribute('aria-expanded', expanded ? 'true' : 'false');
    }

    function toggleCell() {
      var expanded = cell.classList.toggle('nbm-expanded');
      setExpanded(expanded);
    }

    btn.addEventListener('click', toggleCell);

    var outNum = document.createElement('span');
    outNum.className = 'nbm-output-num';
    outNum.textContent = String(idx + 1);
    outNum.setAttribute('role', 'button');
    outNum.setAttribute('tabindex', '0');
    outNum.setAttribute('aria-expanded', 'false');
    outNum.setAttribute('aria-label', 'Toggle code for cell ' + (idx + 1));

    outNum.addEventListener('click', toggleCell);
    outNum.addEventListener('keydown', function (event) {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        toggleCell();
      }
    });

    cell.appendChild(outNum);
    cell.appendChild(btn);
  }

  function init() {
    ensureThemeToggle();
    ensureGlobalControlsToggle();
    var cells = document.querySelectorAll('.cell.code_cell, .jp-CodeCell');
    for (var i = 0; i < cells.length; i += 1) {
      ensureToggle(cells[i], i);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
