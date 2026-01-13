/**
 * Instructor Courses - Filter and Sort functionality
 */
document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('search-input');
    const sortSelect = document.getElementById('sort-select');
    const priceFilters = document.querySelectorAll('input[name="price-filter"]');
    const clearBtn = document.getElementById('clear-filters');
    const container = document.getElementById('courses-container');
    const noResults = document.getElementById('no-results');
    const showingCount = document.getElementById('showing-count');

    if (!container) return;

    function filterAndSort() {
        const searchTerm = searchInput.value.toLowerCase();
        const sortValue = sortSelect.value;
        const priceFilter = document.querySelector('input[name="price-filter"]:checked').value;

        const items = Array.from(container.querySelectorAll('.course-item'));
        let visibleCount = 0;

        // Filter
        items.forEach(item => {
            const title = item.dataset.title;
            const price = parseFloat(item.dataset.price);

            let show = true;

            // Search filter
            if (searchTerm && !title.includes(searchTerm)) {
                show = false;
            }

            // Price filter
            if (priceFilter === 'free' && price > 0) {
                show = false;
            } else if (priceFilter === 'paid' && price === 0) {
                show = false;
            }

            if (show) {
                item.classList.remove('d-none');
                visibleCount++;
            } else {
                item.classList.add('d-none');
            }
        });

        // Sort visible items
        const visibleItems = items.filter(item => !item.classList.contains('d-none'));
        visibleItems.sort((a, b) => {
            switch (sortValue) {
                case 'newest':
                    return parseInt(b.dataset.created) - parseInt(a.dataset.created);
                case 'oldest':
                    return parseInt(a.dataset.created) - parseInt(b.dataset.created);
                case 'title-asc':
                    return a.dataset.title.localeCompare(b.dataset.title);
                case 'title-desc':
                    return b.dataset.title.localeCompare(a.dataset.title);
                case 'price-low':
                    return parseFloat(a.dataset.price) - parseFloat(b.dataset.price);
                case 'price-high':
                    return parseFloat(b.dataset.price) - parseFloat(a.dataset.price);
                default:
                    return 0;
            }
        });

        // Reorder DOM
        visibleItems.forEach(item => container.appendChild(item));

        // Update count and show/hide no results
        showingCount.textContent = visibleCount;
        if (visibleCount === 0) {
            noResults.classList.remove('d-none');
        } else {
            noResults.classList.add('d-none');
        }
    }

    // Event listeners
    searchInput.addEventListener('input', filterAndSort);
    sortSelect.addEventListener('change', filterAndSort);
    priceFilters.forEach(radio => {
        radio.addEventListener('change', filterAndSort);
    });

    clearBtn.addEventListener('click', function () {
        searchInput.value = '';
        sortSelect.value = 'newest';
        document.getElementById('price-all').checked = true;
        filterAndSort();
    });
});
