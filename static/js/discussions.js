document.addEventListener('DOMContentLoaded', function () {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const currentUser = document.querySelector('.container').dataset.currentUser;

    // Helper: Fetch API with CSRF
    async function apiCall(url, method, body = null) {
        const headers = {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        };
        const options = { method, headers };
        if (body) options.body = JSON.stringify(body);

        const response = await fetch(url, options);
        if (!response.ok) throw new Error('API Error');
        return response.json();
    }

    // Voting Logic
    document.querySelectorAll('.vote-btn').forEach(btn => {
        btn.addEventListener('click', async function () {
            const type = this.dataset.type; // 'discussion' or 'reply'
            const id = this.dataset.id;
            const val = parseInt(this.dataset.val);

            // Determine endpoint based on type
            const endpoint = (type === 'discussion')
                ? `/api/${type}s/${id}/vote/`
                : `/api/replies/${id}/vote/`;

            try {
                await apiCall(endpoint, 'POST', { vote_type: val });

                // Optimistic UI Update (simple)
                // ideally fetch fresh count or just toggle styling
                // For now, reloading page or checking if count available from response
                // Response doesn't return count currently, let's just toggle active class

                // Toggle active state locally
                const parent = this.parentElement;
                parent.querySelectorAll('.vote-btn').forEach(b => b.classList.remove('active'));
                this.classList.add('active');

                // Real implementation should fetch updated count or increment/decrement locally
                location.reload();

            } catch (error) {
                console.error('Vote failed:', error);
                alert('Failed to vote. Please try again.');
            }
        });
    });

    // Mark as Answer Logic
    document.querySelectorAll('.mark-answer-btn').forEach(btn => {
        btn.addEventListener('click', async function () {
            if (!confirm('Mark this reply as the answer?')) return;

            const id = this.dataset.id;
            try {
                await apiCall(`/api/replies/${id}/mark_answer/`, 'POST');
                location.reload();
            } catch (error) {
                console.error('Mark answer failed:', error);
                alert('Failed to mark answer.');
            }
        });
    });
});
