document.addEventListener('DOMContentLoaded', function () {
    const lessonType = document.getElementById('lesson_type');
    const sections = {
        'text': document.getElementById('text-content-section'),
        'video': document.getElementById('video-content-section'),
        'quiz': document.getElementById('quiz-content-section')
    };

    function updateSections() {
        const selectedType = lessonType.value;
        Object.entries(sections).forEach(([type, section]) => {
            if (section) {
                section.style.display = type === selectedType ? 'block' : 'none';
            }
        });

        // Re-initialize TinyMCE when switching to text section
        if (selectedType === 'text') {
            if (typeof tinymce !== 'undefined') {
                // Check if editor already exists
                const editor = tinymce.get('lesson_content');
                if (!editor) {
                    //Use shared TinyMCE configuration
                    if (window.tinyMceConfig) {
                        tinymce.init({
                            ...window.tinyMceConfig,
                            selector: '#lesson_content'
                        });
                    }
                }
            }
        }
    }

    if (lessonType) {
        lessonType.addEventListener('change', updateSections);
    }

    // Initialize TinyMCE on page load if it's a text lesson
    if (lessonType && lessonType.value === 'text') {
        if (typeof tinymce !== 'undefined') {
            //Use shared TinyMCE configuration
            if (window.tinyMceConfig) {
                tinymce.init({
                    ...window.tinyMceConfig,
                    selector: '#lesson_content'
                });
            }
        }
    }

    // Ensure TinyMCE content is synced before form submission
    const lessonForm = document.querySelector('form');
    if (lessonForm) {
        lessonForm.addEventListener('submit', function (e) {
            if (typeof tinymce !== 'undefined') {
                const editor = tinymce.get('lesson_content');
                if (editor) {
                    editor.save(); // Sync content to textarea
                    // Also update the textarea directly to ensure content is there
                    const textarea = document.getElementById('lesson_content');
                    if (textarea) {
                        textarea.value = editor.getContent();
                    }
                }
            }
        });
    }

    // Handle video preview modal
    const videoModal = document.getElementById('deleteVideoModal');
    if (videoModal) {
        videoModal.addEventListener('hidden.bs.modal', function () {
            const videoPlayer = document.getElementById('videoPlayer');
            if (videoPlayer) {
                videoPlayer.pause();
                videoPlayer.currentTime = 0;
            }
        });
    }

    // Preview video file if uploaded
    const videoFileInput = document.getElementById('lesson_video_file');
    const videoPreviewContainer = document.getElementById('video-preview-container');
    if (videoFileInput && videoPreviewContainer) {
        videoFileInput.addEventListener('change', function (e) {
            const file = e.target.files[0];
            if (file) {
                const videoURL = URL.createObjectURL(file);
                videoPreviewContainer.innerHTML = `
                    <div class="mt-3">
                        <h6>Video Preview:</h6>
                        <video controls class="w-100" style="max-height: 300px;">
                            <source src="${videoURL}" type="${file.type}">
                            Your browser does not support the video tag.
                        </video>
                    </div>
                `;
            } else {
                videoPreviewContainer.innerHTML = '';
            }
        });
    }

    // Handle URL/File toggle
    const videoUrlInput = document.getElementById('lesson_video_url');
    if (videoUrlInput && videoFileInput) {
        videoUrlInput.addEventListener('input', function () {
            if (this.value) {
                videoFileInput.disabled = true;
                videoFileInput.value = '';
                videoPreviewContainer.innerHTML = '';
            } else {
                videoFileInput.disabled = false;
            }
        });

        videoFileInput.addEventListener('input', function () {
            if (this.value) {
                videoUrlInput.disabled = true;
                videoUrlInput.value = '';
            } else {
                videoUrlInput.disabled = false;
            }
        });

        // Initial check
        if (videoUrlInput.value) {
            videoFileInput.disabled = true;
        }
        if (videoFileInput.files.length > 0) {
            videoUrlInput.disabled = true;
        }
    }

    // Initialize question handlers
    initializeQuestionHandlers();

    // Handle delete question buttons
    var deleteQuestionButtons = document.querySelectorAll('[data-bs-target^="#deleteQuestionModal"]');
    deleteQuestionButtons.forEach(function (button) {
        button.addEventListener('click', function () {
            var questionId = this.getAttribute('data-question-id');
            var questionText = this.getAttribute('data-question-text');

            // Update modal content
            var modal = document.getElementById('deleteQuestionModal');
            var itemNameElement = modal.querySelector('[data-item-name]');
            if (itemNameElement) {
                itemNameElement.textContent = '"' + questionText + '"';
            }

            // Update form action
            var form = document.getElementById('deleteQuestionForm' + questionId);
            var modalForm = modal.querySelector('form');
            if (modalForm && form) {
                // Get the action from the hidden form
                var action = form.getAttribute('action');
                if (action) {
                    modalForm.setAttribute('action', action);
                }

                // Clear existing hidden inputs
                var existingHiddenInputs = modalForm.querySelectorAll('input[type="hidden"]');
                existingHiddenInputs.forEach(function (input) {
                    modalForm.removeChild(input);
                });

                // Copy hidden inputs from the hidden form
                var hiddenInputs = form.querySelectorAll('input[type="hidden"]');
                hiddenInputs.forEach(function (input) {
                    var newInput = document.createElement('input');
                    newInput.type = 'hidden';
                    newInput.name = input.name;
                    newInput.value = input.value;
                    modalForm.appendChild(newInput);
                });
            }
        });
    });
});

// Load question handlers module
function loadQuestionHandlers() {
    const script = document.createElement('script');
    script.src = '/static/courses/includes/question_handlers.js';
    document.head.appendChild(script);
}

// Load the question handlers
loadQuestionHandlers();

// Enable drag and drop for quiz questions (using jQuery)
$(document).ready(function () {
    const questionsContainer = $('.sortable-questions');

    if (questionsContainer.length > 0) {
        const courseSlug = questionsContainer.data('course-slug');
        const moduleId = questionsContainer.data('module-id');
        const lessonId = questionsContainer.data('lesson-id');
        const quizId = questionsContainer.data('quiz-id');

        // Initialize question sortable using utility function
        initQuestionSortable({
            courseSlug: courseSlug,
            moduleId: moduleId,
            lessonId: lessonId,
            quizId: quizId
        });
    }
});