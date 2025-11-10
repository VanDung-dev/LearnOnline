$(document).ready(function() {
    // Initialize TinyMCE for course description
    if (typeof tinymce !== 'undefined') {
        const descriptionFieldId = $('#id_description').attr('id');
        if (descriptionFieldId) {
            // Use shared TinyMCE configuration
            initSharedTinyMCE('#' + descriptionFieldId, 1000);
        }
    }

    // Ensure TinyMCE content is synced before form submission
    const courseForm = document.getElementById('course-edit-form');
    if (courseForm) {
        courseForm.addEventListener('submit', function(e) {
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

    // Initialize sortable for modules
    const courseSlug = $('.sortable-modules').data('course-slug');
    if (courseSlug) {
        initModuleSortable(courseSlug);

        // Initialize sortable for all lessons
        initAllLessonSortables(courseSlug);
    }
    
    // Handle lesson type changes in create lesson modals
    $('select[id^="lesson_type_"]').each(function() {
        const moduleId = $(this).attr('id').split('_').pop();
        const textSection = $(`#text-content-section-${moduleId}`);
        const videoSection = $(`#video-content-section-${moduleId}`);
        const quizSection = $(`#quiz-content-section-${moduleId}`);
        
        $(this).on('change', function() {
            // Hide all sections
            textSection.hide();
            videoSection.hide();
            quizSection.hide();
            
            // Show the relevant section based on selection
            switch($(this).val()) {
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

// Video handling functions for preview in list
function loadVideoFile(videoFileUrl) {
    const videoFrame = document.getElementById('videoFrame');
    const videoPlayer = document.getElementById('videoPlayer');
    
    // Hide iframes and show video player
    videoFrame.style.display = 'none';
    videoPlayer.style.display = 'block';
    
    // Set the source for the video player
    videoPlayer.src = videoFileUrl;
}

// Stop video when modal is closed
document.addEventListener('DOMContentLoaded', function() {
    const videoModal = document.getElementById('videoModal');
    if (videoModal) {
        videoModal.addEventListener('hidden.bs.modal', function () {
            const videoFrame = document.getElementById('videoFrame');
            const videoPlayer = document.getElementById('videoPlayer');
            
            if (videoFrame) {
                videoFrame.src = '';
            }
            
            if (videoPlayer) {
                videoPlayer.pause();
                videoPlayer.currentTime = 0;
            }
        });
    }
});