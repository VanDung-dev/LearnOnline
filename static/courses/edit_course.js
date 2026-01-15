$(document).ready(function () {
    // Initialize TinyMCE for course description
    // Handled by base.html via .tinymce-editor class or inline script

    // Ensure TinyMCE content is synced before form submission
    const courseForm = document.getElementById('course-edit-form');
    if (courseForm) {
        courseForm.addEventListener('submit', function (e) {
            if (typeof tinymce !== 'undefined') {
                const descriptionFieldId = $('#id_description').attr('id');
                if (descriptionFieldId) {
                    const editor = tinymce.get(descriptionFieldId);
                    if (editor) {
                        editor.save(); // Sync content to textarea
                    }
                }
            }
        });
    }

    // Initialize sortable for sections
    const courseSlug = $('.sortable-sections').data('course-slug');
    if (courseSlug) {
        initSectionSortable(courseSlug);

        // Initialize sortable for all lessons
        initAllLessonSortables(courseSlug);
    }

    // Handle lesson type changes in create lesson modals
    $('select[id^="lesson_type_"]').each(function () {
        const sectionId = $(this).attr('id').split('_').pop();
        const textSection = $(`#text-content-section-${sectionId}`);
        const videoSection = $(`#video-content-section-${sectionId}`);
        const quizSection = $(`#quiz-content-section-${sectionId}`);

        $(this).on('change', function () {
            // Hide all sections
            textSection.hide();
            videoSection.hide();
            quizSection.hide();

            // Show the relevant section based on selection
            switch ($(this).val()) {
                case 'text':
                    textSection.show();
                    break;
                case 'video':
                    videoSection.show();
                    break;
                case 'quiz':
                    quizSection.show();
                    break;
            }
        });
    });
});
