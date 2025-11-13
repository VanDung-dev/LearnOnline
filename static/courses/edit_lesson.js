document.addEventListener('DOMContentLoaded', function() {
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
                    initSharedTinyMCE('#lesson_content', 1000);
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
            initSharedTinyMCE('#lesson_content', 1000);
        }
    }

    // Ensure TinyMCE content is synced before form submission
    const lessonForm = document.querySelector('form');
    if (lessonForm) {
        lessonForm.addEventListener('submit', function(e) {
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
        videoModal.addEventListener('hidden.bs.modal', function() {
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
        videoFileInput.addEventListener('change', function(e) {
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
        videoUrlInput.addEventListener('input', function() {
            if (this.value) {
                videoFileInput.disabled = true;
                videoFileInput.value = '';
                videoPreviewContainer.innerHTML = '';
            } else {
                videoFileInput.disabled = false;
            }
        });

        videoFileInput.addEventListener('input', function() {
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
    
    // Add new answer functionality
    document.addEventListener('click', function(e) {
        // Handle add new answer for new question
        if (e.target.id === 'add-new-answer') {
            const container = document.getElementById('new-answers-container');
            if (container) {
                // Count existing answers to set the correct index for the new checkbox
                const existingAnswers = container.querySelectorAll('.answer-item').length;
                const newItem = document.createElement('div');
                newItem.className = 'answer-item mb-2';
                newItem.innerHTML = `
                    <div class="input-group">
                        <input type="text" name="new_answer_text[]" class="form-control" placeholder="Answer text">
                        <div class="input-group-text">
                            <input type="checkbox" name="new_answer_correct[]" value="${existingAnswers}"> Correct
                        </div>
                        <button class="btn btn-outline-danger remove-answer" type="button">Remove</button>
                    </div>
                `;
                container.appendChild(newItem);
            }
        } 
        // Handle add new answer for existing questions
        else if (e.target.id && e.target.id.startsWith('add-answer-')) {
            const questionId = e.target.getAttribute('data-question-id');
            const container = document.getElementById(`answers-container-${questionId}`);
            if (container) {
                const newItem = document.createElement('div');
                newItem.className = 'answer-item mb-2';
                newItem.innerHTML = `
                    <div class="input-group">
                        <input type="text" name="new_answer_text_${questionId}[]" class="form-control" placeholder="Answer text">
                        <div class="input-group-text">
                            <input type="checkbox" name="new_answer_correct_${questionId}[]"> Correct
                        </div>
                        <button class="btn btn-outline-danger remove-answer" type="button">Remove</button>
                    </div>
                `;
                container.appendChild(newItem);
            }
        }
    });
    
    // Handle checkbox changes for new answers to ensure only one correct answer for single choice
    document.addEventListener('change', function(e) {
        if (e.target.name === 'new_answer_correct[]' && e.target.checked) {
            // Find the question type for new questions
            const questionTypeSelect = document.querySelector('select[name="question_type"]');
            if (questionTypeSelect && questionTypeSelect.value === 'single') {
                // Uncheck all other checkboxes in the same container
                const container = e.target.closest('#new-answers-container');
                if (container) {
                    const checkboxes = container.querySelectorAll('input[name="new_answer_correct[]"]');
                    checkboxes.forEach(checkbox => {
                        if (checkbox !== e.target) {
                            checkbox.checked = false;
                        }
                    });
                }
            }
        }
    });
    
    // Remove answer functionality
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('remove-answer')) {
            e.target.closest('.answer-item').remove();
        }
    });
    
    // Handle delete question buttons
    var deleteQuestionButtons = document.querySelectorAll('[data-bs-target^="#deleteQuestionModal"]');
    deleteQuestionButtons.forEach(function(button) {
        button.addEventListener('click', function() {
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
                existingHiddenInputs.forEach(function(input) {
                    modalForm.removeChild(input);
                });
                
                // Copy hidden inputs from the hidden form
                var hiddenInputs = form.querySelectorAll('input[type="hidden"]');
                hiddenInputs.forEach(function(input) {
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

// Enable drag and drop for quiz questions (using jQuery)
$(document).ready(function() {
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