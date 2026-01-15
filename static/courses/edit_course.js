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
    // Check for sections with subsections and disable "Add Lesson" button for the section
    $('.sortable-section').each(function () {
        var sectionId = $(this).data('section-id');
        var hasSubsections = $(this).find('.sortable-subsection').length > 0;

        if (hasSubsections) {
            // Find the Add Lesson button for this section
            var addLessonBtn = $(this).find('button[data-bs-target="#createLessonModal' + sectionId + '"]');

            if (addLessonBtn.length > 0) {
                addLessonBtn.prop('disabled', true);
                addLessonBtn.addClass('disabled');
                addLessonBtn.removeClass('btn-outline-primary').addClass('btn-outline-secondary');
                addLessonBtn.attr('title', 'Cannot add lessons directly to a section that has subsections.');
            }
        }

        // SYMMETRIC CHECK: Check for sections with direct lessons and disable "Add Subsection" button
        // Direct lessons are inside .sortable-lessons with data-section-id matching the section
        var hasDirectLessons = $(this).find('.sortable-lessons[data-section-id="' + sectionId + '"] .sortable-lesson').length > 0;

        if (hasDirectLessons) {
            var addSubsectionBtn = $(this).find('button[data-bs-target="#createSubsectionModal' + sectionId + '"]');

            if (addSubsectionBtn.length > 0) {
                addSubsectionBtn.prop('disabled', true);
                addSubsectionBtn.addClass('disabled');
                addSubsectionBtn.removeClass('btn-outline-primary').addClass('btn-outline-secondary');
                addSubsectionBtn.attr('title', 'Cannot add subsections to a section that has direct lessons.');
            }
        }
    });

    // Initialize TinyMCE if config is available
    if (window.tinyMceConfig) {
        tinymce.init({
            ...window.tinyMceConfig,
            selector: '#id_description' // Assuming form.description renders with this ID
        });
    }

});
