/* Catalogue table — search, sort, filter */

(function () {
  let allObjects = [];
  let filtered = [];
  let sortCol = 'constellation';
  let sortDir = 'asc';

  const table = document.getElementById('catalogue-table');
  const tbody = document.getElementById('table-body');
  const searchInput = document.getElementById('search');
  const typeFilter = document.getElementById('filter-type');
  const constFilter = document.getElementById('filter-constellation');
  const clearBtn = document.getElementById('clear-filters');
  const countEl = document.getElementById('count');

  fetch('data/objects.json')
    .then(r => r.json())
    .then(data => {
      allObjects = data;
      populateFilters();
      applyFilters();
    });

  function populateFilters() {
    const types = [...new Set(allObjects.map(o => o.typeLabel))].sort();
    types.forEach(t => {
      const opt = document.createElement('option');
      opt.value = t;
      opt.textContent = t;
      typeFilter.appendChild(opt);
    });

    const consts = [...new Set(allObjects.map(o => o.constellation))].sort();
    consts.forEach(c => {
      const opt = document.createElement('option');
      opt.value = c;
      opt.textContent = c;
      constFilter.appendChild(opt);
    });
  }

  function applyFilters() {
    const query = searchInput.value.toLowerCase().trim();
    const typeVal = typeFilter.value;
    const constVal = constFilter.value;

    filtered = allObjects.filter(o => {
      if (query && !o.name.toLowerCase().includes(query) &&
          !o.constellation.toLowerCase().includes(query) &&
          !o.displayName.toLowerCase().includes(query)) return false;
      if (typeVal && o.typeLabel !== typeVal) return false;
      if (constVal && o.constellation !== constVal) return false;
      return true;
    });

    sortData();
    render();
  }

  function sortData() {
    filtered.sort((a, b) => {
      let va = a[sortCol];
      let vb = b[sortCol];

      if (va === null || va === undefined) va = sortDir === 'asc' ? Infinity : -Infinity;
      if (vb === null || vb === undefined) vb = sortDir === 'asc' ? Infinity : -Infinity;

      if (typeof va === 'string') {
        va = va.toLowerCase();
        vb = (vb || '').toLowerCase();
        if (va < vb) return sortDir === 'asc' ? -1 : 1;
        if (va > vb) return sortDir === 'asc' ? 1 : -1;
        return 0;
      }
      return sortDir === 'asc' ? va - vb : vb - va;
    });
  }

  function render() {
    tbody.innerHTML = '';
    filtered.forEach(o => {
      const tr = document.createElement('tr');
      tr.innerHTML =
        '<td class="obj-name"><a href="' + o.url + '">' + o.name + '</a></td>' +
        '<td><span class="type-badge ' + o.typeCss + '">' + o.typeLabel + '</span></td>' +
        '<td><a href="constellations/' + o.constellationSlug + '.html">' + o.constellation + '</a></td>' +
        '<td>' + o.ra + '</td>' +
        '<td>' + o.dec + '</td>' +
        '<td>' + o.magStr + '</td>' +
        '<td>' + o.size + '</td>' +
        '<td>' + o.sbStr + '</td>';
      tbody.appendChild(tr);
    });
    countEl.textContent = 'Showing ' + filtered.length + ' of ' + allObjects.length + ' objects';
  }

  // Sort on column click
  table.querySelector('thead').addEventListener('click', function (e) {
    const th = e.target.closest('th');
    if (!th || th.classList.contains('no-sort')) return;
    const col = th.dataset.sort;
    if (!col) return;

    if (sortCol === col) {
      sortDir = sortDir === 'asc' ? 'desc' : 'asc';
    } else {
      sortCol = col;
      sortDir = 'asc';
    }

    table.querySelectorAll('th').forEach(h => h.classList.remove('sort-asc', 'sort-desc'));
    th.classList.add(sortDir === 'asc' ? 'sort-asc' : 'sort-desc');

    sortData();
    render();
  });

  // Debounced search
  let debounce;
  searchInput.addEventListener('input', function () {
    clearTimeout(debounce);
    debounce = setTimeout(applyFilters, 250);
  });

  typeFilter.addEventListener('change', applyFilters);
  constFilter.addEventListener('change', applyFilters);
  clearBtn.addEventListener('click', function () {
    searchInput.value = '';
    typeFilter.value = '';
    constFilter.value = '';
    applyFilters();
  });
})();
