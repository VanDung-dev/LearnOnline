
function toggleEdit(type, id) {
    const formId = `edit-form-${type}-${id}`;
    const form = document.getElementById(formId);
    const contentId = (type === 'reply') ? `reply-content-${id}` : null;
    const content = contentId ? document.getElementById(contentId) : null;

    // Toggle form visibility
    if (form.classList.contains('d-none')) {
        form.classList.remove('d-none');
        if (content) content.classList.add('d-none');
    } else {
        form.classList.add('d-none');
        if (content) content.classList.remove('d-none');
    }
}
