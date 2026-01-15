document.addEventListener('DOMContentLoaded', function () {
    const titleInput = document.getElementById('courseTitleInput');
    const submitBtn = document.getElementById('createCourseSubmitBtn');
    const duplicateErrorDiv = document.getElementById('titleDuplicateError');
    const statusSpan = document.getElementById('titleCheckStatus');

    // Get the check URL from the data attribute
    const checkUrl = titleInput.dataset.checkUrl;

    let debounceTimer;

    // Helper to set status icon
    function setStatus(state) {
        let iconHtml = '&nbsp;';
        switch (state) {
            case 'loading':
                iconHtml = '<div class="spinner-border spinner-border-sm text-primary" role="status"><span class="visually-hidden">Loading...</span></div>';
                break;
            case 'success':
                iconHtml = '<i class="bi bi-check-circle-fill text-success"></i>';
                break;
            case 'error':
                iconHtml = '<i class="bi bi-x-circle-fill text-danger"></i>';
                break;
            case 'idle':
                // Idle spinner
                iconHtml = '<div class="spinner-border spinner-border-sm text-secondary" role="status"><span class="visually-hidden">Waiting...</span></div>';
                break;
            case 'empty':
            default:
                iconHtml = '&nbsp;';
                break;
        }
        statusSpan.innerHTML = iconHtml;
    }

    // Reset form when modal is closed
    const modal = document.getElementById('createCourseModal');
    if (modal) {
        modal.addEventListener('hidden.bs.modal', function () {
            titleInput.value = '';
            titleInput.classList.remove('is-valid', 'is-invalid');
            setStatus('empty');
            duplicateErrorDiv.classList.add('d-none');
            submitBtn.disabled = true;
        });
    }

    if (titleInput) {
        titleInput.addEventListener('input', function () {
            const title = this.value.trim();

            // Reset UI
            submitBtn.disabled = true;
            duplicateErrorDiv.classList.add('d-none');
            titleInput.classList.remove('is-valid', 'is-invalid');

            clearTimeout(debounceTimer);

            if (title.length === 0) {
                setStatus('empty');
                return;
            }

            setStatus('idle');

            debounceTimer = setTimeout(() => {
                setStatus('loading');

                // Call API
                fetch(`${checkUrl}?title=` + encodeURIComponent(title))
                    .then(response => response.json())
                    .then(data => {
                        // Check if input has changed while request was in flight
                        if (titleInput.value.trim() !== title) {
                            return;
                        }

                        if (data.exists) {
                            // Duplicate
                            titleInput.classList.add('is-invalid');
                            setStatus('error');
                            duplicateErrorDiv.classList.remove('d-none');
                        } else {
                            // Valid
                            titleInput.classList.add('is-valid');
                            setStatus('success');
                            submitBtn.disabled = false;
                        }
                    })
                    .catch(error => {
                        console.error('Error checking title:', error);
                        setStatus('empty');
                    });
            }, 1000); // 1s debounce
        });
    }
});
