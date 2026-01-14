document.addEventListener('DOMContentLoaded', function () {
    const unreadBadge = document.getElementById('notification-badge');

    // 1. Polling Unread Count
    function fetchUnreadCount() {
        if (!unreadBadge) return;
        fetch('/notifications/api/unread-count/')
            .then(response => {
                if (response.status === 403) return null;
                if (response.ok) return response.json();
                throw new Error('Network response was not ok.');
            })
            .then(data => {
                if (!data) return;
                if (data.count > 0) {
                    unreadBadge.innerText = data.count;
                    unreadBadge.classList.remove('d-none');
                } else {
                    unreadBadge.classList.add('d-none');
                }
            })
            .catch(error => console.log('Notification fetch error:', error));
    }

    if (unreadBadge) {
        fetchUnreadCount();
        setInterval(fetchUnreadCount, 60000);
    }

    // 2. Load Notifications Logic
    const dropdownToggle = document.getElementById('navbarDropdownMenuLink');
    if (dropdownToggle) {
        dropdownToggle.addEventListener('show.bs.dropdown', function () {
            const dropdownMenu = this.nextElementSibling;

            fetch('/notifications/api/list/')
                .then(response => response.json())
                .then(data => {
                    let html = '<li><h6 class="dropdown-header">Notifications</h6></li><li><hr class="dropdown-divider"></li>';

                    // DRF pagination returns data.results, or just data if no pagination
                    const results = data.results || data;

                    if (results.length === 0) {
                        html += '<li><span class="dropdown-item text-muted small">No new notifications</span></li>';
                    } else {
                        results.slice(0, 5).forEach(notif => {
                            const bgClass = notif.is_read ? '' : 'bg-light';
                            const textClass = notif.is_read ? 'text-muted' : 'fw-bold';
                            const link = notif.link || '#';
                            html += `<li><a class="dropdown-item small ${bgClass} ${textClass}" href="#" onclick="markRead(event, ${notif.id}, '${link}')">${notif.title}</a></li>`;
                        });
                    }
                    html += '<li><hr class="dropdown-divider"></li><li><a class="dropdown-item text-center small" href="/notifications/">View all</a></li>';
                    dropdownMenu.innerHTML = html;
                })
                .catch(err => console.error('Error loading notifications', err));
        });
    }

    // Helper: CSRF Token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // 3. Mark Read Function
    window.markRead = function (event, id, link) {
        event.preventDefault(); // Prevent default link behavior first

        fetch(`/notifications/api/${id}/mark-read/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            }
        }).then(response => {
            if (response.ok && link && link !== '#') {
                window.location.href = link;
            }
        });
    }
});
