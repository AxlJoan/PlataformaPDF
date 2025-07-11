let debounceTimeout;

function loadPage(url) {
  fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
    .then(response => response.json())
    .then(data => {
      document.getElementById('logs-table-container').innerHTML = data.html;
      attachPaginationListeners();
    });
}

function attachPaginationListeners() {
  document.querySelectorAll('.pagination a').forEach(link => {
    link.onclick = function(e) {
      e.preventDefault();
      loadPage(this.href);
    };
  });
}

document.getElementById('filter-user').addEventListener('input', function() {
  clearTimeout(debounceTimeout);
  debounceTimeout = setTimeout(() => {
    const user = this.value;
    const action = document.getElementById('filter-action').value;
    const url = `/user-logs/?user=${encodeURIComponent(user)}&action=${encodeURIComponent(action)}`;
    loadPage(url);
  }, 400);
});

document.getElementById('filter-action').addEventListener('change', function() {
  const user = document.getElementById('filter-user').value;
  const action = this.value;
  const url = `/user-logs/?user=${encodeURIComponent(user)}&action=${encodeURIComponent(action)}`;
  loadPage(url);
});

// Inicializar
attachPaginationListeners();
