document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");
    if (!form) return;

    const titleInput = document.getElementById("id_title");
    const bodyInput = document.getElementById("id_body");

    // Get course slug from data attribute on the form
    const courseSlug = form.getAttribute("data-course-slug");
    if (!courseSlug) {
        console.error("Course slug not found in form data attributes.");
        return;
    }

    // Create a unique key for this course's discussion draft
    const STORAGE_KEY = "discussion_draft_" + courseSlug;

    // Function to get current content from inputs/TinyMCE
    function getFormValues() {
        let bodyValue = bodyInput ? bodyInput.value : '';
        // If TinyMCE is active, get content from it
        if (typeof tinymce !== 'undefined' && tinymce.get('id_body')) {
            bodyValue = tinymce.get('id_body').getContent();
        }
        return {
            title: titleInput ? titleInput.value : '',
            body: bodyValue
        };
    }

    // Restore draft if exists and fields are empty (don't overwrite server-rendered data)
    const savedDraft = localStorage.getItem(STORAGE_KEY);
    if (savedDraft) {
        try {
            const data = JSON.parse(savedDraft);

            // Restore Title
            if (titleInput && !titleInput.value && data.title) {
                titleInput.value = data.title;
            }

            // Restore Body
            if (bodyInput && !bodyInput.value && data.body) {
                bodyInput.value = data.body;
                // If TinyMCE is initialized, update it too
                if (typeof tinymce !== 'undefined' && tinymce.get('id_body')) {
                    tinymce.get('id_body').setContent(data.body);
                }
            }
        } catch (e) {
            console.error("Error restoring discussion draft:", e);
        }
    }

    // Auto-save draft every 1 second
    setInterval(() => {
        const data = getFormValues();
        // Only save if there's actually some content to save
        if (data.title || data.body) {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
        }
    }, 1000);

    // Clear cache on submit
    form.addEventListener("submit", function () {
        localStorage.removeItem(STORAGE_KEY);
    });
});
