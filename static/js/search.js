 
// ===== Live Search with Debounce =====
function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

document.addEventListener('DOMContentLoaded', function() {
    const searchInputs = document.querySelectorAll('[data-live-search]');

    searchInputs.forEach(function(input) {
        const targetTable = document.getElementById(input.dataset.liveSearch);

        if (targetTable) {
            input.addEventListener('input', debounce(function() {
                const query = this.value.toLowerCase().trim();
                const rows = targetTable.querySelectorAll('tbody tr');

                rows.forEach(function(row) {
                    const text = row.textContent.toLowerCase();
                    row.style.display = text.includes(query) ? '' : 'none';
                });

                // Show/hide empty message
                const visibleRows = targetTable.querySelectorAll('tbody tr:not([style*="display: none"])');
                let emptyMsg = targetTable.querySelector('.search-empty');
                if (visibleRows.length === 0) {
                    if (!emptyMsg) {
                        emptyMsg = document.createElement('tr');
                        emptyMsg.className = 'search-empty';
                        emptyMsg.innerHTML = '<td colspan="100" style="text-align:center;padding:20px;color:#94a3b8;">No results found</td>';
                        targetTable.querySelector('tbody').appendChild(emptyMsg);
                    }
                } else if (emptyMsg) {
                    emptyMsg.remove();
                }
            }, 300));
        }
    });
});