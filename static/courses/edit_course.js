$(document).ready(function() {
    // Enable sorting for modules
    $('.sortable-modules').sortable({
        handle: '.handle',
        update: function(event, ui) {
            const moduleIds = [];
            $('.sortable-module').each(function() {
                moduleIds.push($(this).data('module-id'));
            });
            
            const courseSlug = $('.sortable-modules').data('course-slug');
            
            console.log('Sending module order:', moduleIds);
            console.log('Course slug:', courseSlug);
            
            // Show a temporary message
            const originalText = $('.text-muted:contains("Drag and drop modules")').text();
            $('.text-muted:contains("Drag and drop modules")').text('Saving module order...');
            
            // Send AJAX request to update module order
            $.ajax({
                url: `/instructor/courses/${encodeURIComponent(courseSlug)}/modules/reorder/`,
                method: 'POST',
                headers: {
                    'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val(),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                data: {
                    module_order: moduleIds
                },
                success: function(response) {
                    console.log('Server response:', response);
                    if (response.status === 'success') {
                        console.log('Modules reordered successfully');
                        $('.text-muted:contains("Saving module order")').text('Module order saved successfully!');
                        setTimeout(function() {
                            $('.text-muted:contains("Module order saved")').text(originalText);
                        }, 2000);
                    } else {
                        console.error('Error reordering modules:', response.message);
                        $('.text-muted:contains("Saving module order")').text('Error saving module order: ' + response.message);
                        // Revert the sort
                        $('.sortable-modules').sortable('cancel');
                    }
                },
                error: function(xhr, status, error) {
                    console.error('AJAX error:', error);
                    console.error('Response text:', xhr.responseText);
                    $('.text-muted:contains("Saving module order")').text('Error saving module order. Check console for details.');
                    // Revert the sort
                    $('.sortable-modules').sortable('cancel');
                }
            });
        }
    });
    
    // Enable sorting for each module's lessons
    $('.sortable-lessons').each(function() {
        const moduleId = $(this).data('module-id');
        const list = $(this).find('.lesson-list');
        const courseSlug = window.courseSlug; // This will be set from the template
        
        list.sortable({
            handle: '.handle',
            update: function(event, ui) {
                const lessonIds = [];
                list.find('.sortable-lesson').each(function() {
                    lessonIds.push($(this).data('lesson-id'));
                });
                
                console.log('Sending lesson order:', lessonIds);
                console.log('Module ID:', moduleId);
                console.log('Course slug:', courseSlug);
                
                // Show a temporary message
                const originalText = $('.text-muted:contains("Drag and drop lessons")').text();
                $('.text-muted:contains("Drag and drop lessons")').text('Saving order...');
                
                // Send AJAX request to update order
                $.ajax({
                    url: `/instructor/courses/${encodeURIComponent(courseSlug)}/modules/${moduleId}/lessons/reorder/`,
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val(),
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    data: {
                        lesson_order: lessonIds
                    },
                    success: function(response) {
                        console.log('Server response:', response);
                        if (response.status === 'success') {
                            console.log('Lessons reordered successfully');
                            $('.text-muted:contains("Saving order")').text('Order saved successfully!');
                            setTimeout(function() {
                                $('.text-muted:contains("Order saved")').text(originalText);
                            }, 2000);
                        } else {
                            console.error('Error reordering lessons:', response.message);
                            $('.text-muted:contains("Saving order")').text('Error saving order: ' + response.message);
                            // Revert the sort
                            list.sortable('cancel');
                        }
                    },
                    error: function(xhr, status, error) {
                        console.error('AJAX error:', error);
                        console.error('Response text:', xhr.responseText);
                        $('.text-muted:contains("Saving order")').text('Error saving order. Check console for details.');
                        // Revert the sort
                        list.sortable('cancel');
                    }
                });
            }
        });
        
        list.disableSelection();
    });
    
    $('.sortable-modules').disableSelection();
    
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
    
    // Handle lesson type changes in edit lesson modals
    $('select[id^="edit_lesson_type_"]').each(function() {
        const lessonId = $(this).attr('id').split('_').pop();
        const textSection = $(`#edit-text-content-section-${lessonId}`);
        const videoSection = $(`#edit-video-content-section-${lessonId}`);
        const quizSection = $(`#edit-quiz-content-section-${lessonId}`);
        
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

// Video handling functions
function loadVideo(videoUrl) {
    const videoFrame = document.getElementById('videoFrame');
    const videoPlayer = document.getElementById('videoPlayer');
    
    // Hide both iframes and video players
    videoFrame.style.display = 'none';
    videoPlayer.style.display = 'none';
    
    // Check if it's a YouTube URL
    if (videoUrl.includes('youtube.com') || videoUrl.includes('youtu.be')) {
        // Convert YouTube URLs to embed if needed
        let embedUrl = videoUrl;
        if (videoUrl.includes('youtube.com/watch')) {
            const videoId = videoUrl.split('v=')[1];
            const ampersandPosition = videoId.indexOf('&');
            if (ampersandPosition !== -1) {
                embedUrl = 'https://www.youtube.com/embed/' + videoId.substring(0, ampersandPosition);
            } else {
                embedUrl = 'https://www.youtube.com/embed/' + videoId;
            }
        } else if (videoUrl.includes('youtu.be')) {
            const videoId = videoUrl.split('youtu.be/')[1];
            embedUrl = 'https://www.youtube.com/embed/' + videoId;
        }
        
        videoFrame.src = embedUrl;
        videoFrame.style.display = 'block';
    } 
    // Check if it's a Vimeo URL
    else if (videoUrl.includes('vimeo.com')) {
        const videoId = videoUrl.split('vimeo.com/')[1];
        const embedUrl = 'https://player.vimeo.com/video/' + videoId;
        videoFrame.src = embedUrl;
        videoFrame.style.display = 'block';
    }
    // Other platforms can be added here
    else {
        videoFrame.src = videoUrl;
        videoFrame.style.display = 'block';
    }
}

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
    document.getElementById('videoModal').addEventListener('hidden.bs.modal', function () {
        const videoFrame = document.getElementById('videoFrame');
        const videoPlayer = document.getElementById('videoPlayer');
        
        // Stop iframe by deleting src
        videoFrame.src = '';
        
        // Stop the video player and reset the time
        videoPlayer.pause();
        videoPlayer.currentTime = 0;
    });
});