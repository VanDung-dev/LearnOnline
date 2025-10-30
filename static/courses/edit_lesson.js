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
});