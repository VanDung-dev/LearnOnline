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
                url: `/instructor/courses/${encodeURIComponent(courseSlug)}/reorder/`,
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