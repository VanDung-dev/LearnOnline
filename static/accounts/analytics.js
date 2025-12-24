document.addEventListener('DOMContentLoaded', function () {
    initStudentAnalytics();
    initInstructorAnalytics();
});

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
