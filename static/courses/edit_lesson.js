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
    }

    if (lessonType) {
        lessonType.addEventListener('change', updateSections);
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
    
    // Add new answer in add question modal
    const addNewAnswerButton = document.getElementById('add-new-answer');
    if (addNewAnswerButton) {
        addNewAnswerButton.addEventListener('click', function() {
            const container = document.getElementById('new-answers-container');
            const newItem = document.createElement('div');
            newItem.className = 'answer-item mb-2';
            newItem.innerHTML = `
                <div class="input-group">
                    <input type="text" name="new_answer_text[]" class="form-control" placeholder="Answer text">
                    <div class="input-group-text">
                        <input type="checkbox" name="new_answer_correct[]"> Correct
                    </div>
                    <button class="btn btn-outline-danger remove-answer" type="button">Remove</button>
                </div>
            `;
            container.appendChild(newItem);
        });
    }
    
    // Add new answer in edit question modals
    document.querySelectorAll('.add-answer').forEach(button => {
        button.addEventListener('click', function() {
            const questionId = this.getAttribute('data-question-id');
            const container = document.getElementById(`answers-container-${questionId}`);
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
        });
    });
    
    // Remove answer functionality
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('remove-answer')) {
            e.target.closest('.answer-item').remove();
        }
    });
});