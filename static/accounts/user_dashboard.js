document.addEventListener('DOMContentLoaded', function () {
    // Universal Filter/Sort Logic for Dashboard
    initDashboardFilters();

    // Analytics Initialization
    initStudentAnalytics();
    initInstructorAnalytics();

    // Fix for Chart.js rendering in hidden Bootstrap tabs
    var tabEls = document.querySelectorAll('a[data-bs-toggle="list"]');
    tabEls.forEach(function (tabEl) {
        tabEl.addEventListener('shown.bs.tab', function (event) {
            // Trigger window resize to force Chart.js to update
            window.dispatchEvent(new Event('resize'));
        });
    });
});

function initDashboardFilters() {
    const searchInput = document.getElementById('search-input');
    const sortSelect = document.getElementById('sort-select');
    const statusFilters = document.querySelectorAll('input[name="status-filter"]'); // Student
    const priceFilters = document.querySelectorAll('input[name="price-filter"]'); // Instructor
    const coursesContainer = document.getElementById('courses-container');
    const noResultsMsg = document.getElementById('no-results');

    if (!coursesContainer) return; // Exit if no course container (e.g. empty state)

    // Helper to get all course items
    const getItems = () => Array.from(document.querySelectorAll('.course-item'));

    function filterAndSort() {
        const searchTerm = searchInput ? searchInput.value.toLowerCase() : '';
        const sortValue = sortSelect ? sortSelect.value : 'newest';

        // Get active filter value (handle optional filters)
        let statusValue = 'all';
        let priceValue = 'all';

        const activeStatus = document.querySelector('input[name="status-filter"]:checked');
        if (activeStatus) statusValue = activeStatus.value;

        const activePrice = document.querySelector('input[name="price-filter"]:checked');
        if (activePrice) priceValue = activePrice.value;

        let visibleCount = 0;

        getItems().forEach(item => {
            const title = item.dataset.title;
            const status = item.dataset.status; // might be undefined for instructor
            const price = parseFloat(item.dataset.price); // might be NaN for student

            let matchesSearch = !searchTerm || title.includes(searchTerm);
            let matchesStatus = (statusValue === 'all') || (status === statusValue);

            let matchesPrice = true;
            if (priceValue === 'free') matchesPrice = (price === 0);
            if (priceValue === 'paid') matchesPrice = (price > 0);

            if (matchesSearch && matchesStatus && matchesPrice) {
                item.classList.remove('d-none');
                visibleCount++;
            } else {
                item.classList.add('d-none');
            }
        });

        if (visibleCount === 0 && getItems().length > 0) {
            if (noResultsMsg) noResultsMsg.classList.remove('d-none');
        } else {
            if (noResultsMsg) noResultsMsg.classList.add('d-none');
        }

        sortItems(sortValue);
    }

    function sortItems(sortValue) {
        const items = getItems();

        items.sort((a, b) => {
            const titleA = a.dataset.title;
            const titleB = b.dataset.title;
            const dateA = parseInt(a.dataset.created || a.dataset.enrolled || 0);
            const dateB = parseInt(b.dataset.created || b.dataset.enrolled || 0);
            const priceA = parseFloat(a.dataset.price || 0);
            const priceB = parseFloat(b.dataset.price || 0);

            switch (sortValue) {
                case 'title-asc': return titleA.localeCompare(titleB);
                case 'title-desc': return titleB.localeCompare(titleA);
                case 'newest': return dateB - dateA;
                case 'oldest': return dateA - dateB;
                case 'price-low': return priceA - priceB;
                case 'price-high': return priceB - priceA;
                default: return 0;
            }
        });

        // Re-append items in new order
        items.forEach(item => coursesContainer.appendChild(item));
    }

    // Event Listeners
    if (searchInput) searchInput.addEventListener('input', filterAndSort);
    if (sortSelect) sortSelect.addEventListener('change', filterAndSort);
    statusFilters.forEach(radio => radio.addEventListener('change', filterAndSort));
    priceFilters.forEach(radio => radio.addEventListener('change', filterAndSort));

    // Initial sort
    filterAndSort();
}

function initStudentAnalytics() {
    const ctx = document.getElementById('studentProgressChart');
    if (!ctx) return;

    fetch('/analytics/api/student-progress/')
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            if (data.length === 0) {
                // Handle no data case
                ctx.parentElement.innerHTML = '<p class="text-muted text-center">No enrolled courses yet.</p>';
                return;
            }

            const labels = data.map(item => item.course_title);
            const values = data.map(item => item.progress_percent);
            const colors = values.map(val => val === 100 ? '#198754' : '#0d6efd'); // Green if 100%, else Blue

            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Progress (%)',
                        data: values,
                        backgroundColor: colors,
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100
                        }
                    },
                    plugins: {
                        legend: {
                            display: false
                        },
                        title: {
                            display: true,
                            text: 'Your Course Progress'
                        }
                    }
                }
            });
        })
        .catch(error => console.error('Error fetching student analytics:', error));
}

function initInstructorAnalytics() {
    const ctx = document.getElementById('instructorRevenueChart');
    if (!ctx) return;

    fetch('/analytics/api/instructor-stats/')
        .then(response => {
            if (response.status === 403) throw new Error('Unauthorized');
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            // Update Summary Cards if they exist
            if (document.getElementById('total-students'))
                document.getElementById('total-students').innerText = data.total_students;
            if (document.getElementById('total-revenue'))
                document.getElementById('total-revenue').innerText = '$' + data.total_revenue;

            // Prepare Chart Data
            // monthly_enrollments is list of {month: "2023-01-01...", count: 5}
            const labels = data.monthly_enrollments.map(item => {
                const date = new Date(item.month);
                return date.toLocaleDateString('default', { month: 'short', year: 'numeric' });
            });
            const counts = data.monthly_enrollments.map(item => item.count);

            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'New Enrollments',
                        data: counts,
                        borderColor: '#0d6efd',
                        backgroundColor: 'rgba(13, 110, 253, 0.1)',
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Monthly Enrollment Trend'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                precision: 0
                            }
                        }
                    }
                }
            });
        })
        .catch(error => console.error('Error fetching instructor analytics:', error));
}
