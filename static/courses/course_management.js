$(document).ready(function() {
    // Show a notification message
    function showNotification(message, type = 'info') {
        // Create a temporary alert element
        const alertClass = type === 'error' ? 'alert-danger' : 
                          type === 'success' ? 'alert-success' : 'alert-info';
        
        const alertHtml = `
            <div class="alert ${alertClass} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3" 
                 style="z-index: 9999;" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
        
        // Remove any existing notifications
        $('.alert').remove();
        
        // Add the new notification to the body
        $('body').append(alertHtml);
        
        // Auto-hide after 3 seconds
        setTimeout(() => {
            $('.alert').fadeOut(() => {
                $('.alert').remove();
            });
        }, 3000);
    }
    
    // Handle thumbnail preview
    $('#id_thumbnail').on('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                // Check if preview container already exists
                let previewContainer = $('#thumbnail-preview');
                if (previewContainer.length === 0) {
                    // Create preview container if it doesn't exist
                    $('#thumbnail-preview-container').append(`
                        <div id="thumbnail-preview" class="mt-2">
                            <small class="form-text text-muted">Preview:</small>
                            <img src="${e.target.result}" alt="Thumbnail preview" class="img-thumbnail" style="max-height: 150px;">
                        </div>
                    `);
                } else {
                    // Update existing preview
                    previewContainer.find('img').attr('src', e.target.result);
                }
                
                // Hide current thumbnail if exists
                $('#current-thumbnail').hide();
            };
            reader.readAsDataURL(file);
        } else {
            // Remove preview if no file is selected
            $('#thumbnail-preview').remove();
            // Show current thumbnail if exists
            $('#current-thumbnail').show();
        }
    });
    
    // Handle thumbnail deletion via AJAX
    $('#delete-thumbnail-btn').on('click', function() {
        const button = $(this);
        const originalText = button.text();
        
        // Show loading state
        button.prop('disabled', true).text('Deleting...');
        
        $.ajax({
            url: window.location.href,
            method: 'POST',
            data: {
                'delete_thumbnail': 'true',
                'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
            },
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            success: function(response) {
                if (response.status === 'success') {
                    showNotification(response.message, 'success');
                    // Remove the current thumbnail display
                    $('#current-thumbnail').remove();
                    // If there's a preview, remove it too
                    $('#thumbnail-preview').remove();
                    // Reset the file input
                    $('#id_thumbnail').val('');
                } else {
                    showNotification(response.message || 'Error deleting thumbnail', 'error');
                    button.prop('disabled', false).text(originalText);
                }
            },
            error: function(xhr, status, error) {
                showNotification('Error deleting thumbnail. Please try again.', 'error');
                button.prop('disabled', false).text(originalText);
                console.error('Error deleting thumbnail:', error);
            }
        });
    });
    
    // Handle course editing via AJAX
    $('#course-edit-form').on('submit', function(e) {
        // Only handle AJAX if it's not a delete_thumbnail action
        if ($('#delete-thumbnail-btn').is(':focus')) {
            return; // Let it proceed normally for thumbnail deletion
        }
        
        e.preventDefault();
        
        const form = $(this);
        const formData = new FormData(form[0]);
        const submitButton = $('#course-save-btn');
        const originalButtonText = submitButton.text();
        
        // Show loading state
        submitButton.prop('disabled', true).text('Updating...');
        
        $.ajax({
            url: window.location.href, // Current page URL
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            headers: {
                'X-CSRFToken': form.find('[name=csrfmiddlewaretoken]').val(),
                'X-Requested-With': 'XMLHttpRequest'
            },
            success: function(response) {
                if (response.status === 'success') {
                    showNotification(response.message, 'success');
                    // Reload page to show updated thumbnail
                    setTimeout(() => location.reload(), 1500);
                } else {
                    showNotification(response.message || 'Error updating course', 'error');
                }
                submitButton.prop('disabled', false).text(originalButtonText);
            },
            error: function(xhr, status, error) {
                showNotification('Error updating course. Please try again.', 'error');
                submitButton.prop('disabled', false).text(originalButtonText);
                console.error('Error updating course:', error);
            }
        });
    });
    
    // Handle course deletion via AJAX
    $('#deleteCourseModal form').on('submit', function(e) {
        e.preventDefault();
        
        const form = $(this);
        const modal = $('#deleteCourseModal');
        const submitButton = form.find('button[type="submit"]');
        const originalButtonText = submitButton.text();
        
        // Show loading state
        submitButton.prop('disabled', true).text('Deleting...');
        
        $.ajax({
            url: form.attr('action'),
            method: 'POST',
            data: form.serialize(),
            headers: {
                'X-CSRFToken': form.find('[name=csrfmiddlewaretoken]').val(),
                'X-Requested-With': 'XMLHttpRequest'
            },
            success: function(response) {
                if (response.status === 'success') {
                    showNotification(response.message, 'success');
                    // Close the modal
                    modal.modal('hide');
                    // Redirect to instructor courses page
                    setTimeout(() => {
                        window.location.href = response.redirect_url || '/instructor/courses/';
                    }, 1500);
                } else {
                    showNotification(response.message || 'Error deleting course', 'error');
                    submitButton.prop('disabled', false).text(originalButtonText);
                }
            },
            error: function(xhr, status, error) {
                showNotification('Error deleting course. Please try again.', 'error');
                submitButton.prop('disabled', false).text(originalButtonText);
                console.error('Error deleting course:', error);
            }
        });
    });
    
    // Handle section creation via AJAX
    $('#createSectionModal form').on('submit', function(e) {
        e.preventDefault();
        
        const form = $(this);
        const formData = new FormData(form[0]);
        const modal = $('#createSectionModal');
        const submitButton = form.find('button[type="submit"]');
        const originalButtonText = submitButton.text();
        
        // Show loading state
        submitButton.prop('disabled', true).text('Creating...');
        
        $.ajax({
            url: form.attr('action'),
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            headers: {
                'X-CSRFToken': form.find('[name=csrfmiddlewaretoken]').val(),
                'X-Requested-With': 'XMLHttpRequest'
            },
            success: function(response) {
                if (response.status === 'success') {
                    showNotification(response.message, 'success');
                    // Close the modal
                    modal.modal('hide');
                    // Reset the form
                    form[0].reset();
                    // Reload the page to show the new section
                    setTimeout(() => location.reload(), 1000);
                } else {
                    showNotification(response.message || 'Error creating section', 'error');
                    submitButton.prop('disabled', false).text(originalButtonText);
                }
            },
            error: function(xhr, status, error) {
                showNotification('Error creating section. Please try again.', 'error');
                submitButton.prop('disabled', false).text(originalButtonText);
                console.error('Error creating section:', error);
            }
        });
    });
    
    // Handle section editing via AJAX
    $('[id^="editSectionModal"] form').on('submit', function(e) {
        e.preventDefault();
        
        const form = $(this);
        const formData = new FormData(form[0]);
        const modalId = form.closest('.modal').attr('id');
        const modal = $('#' + modalId);
        const submitButton = form.find('button[type="submit"]');
        const originalButtonText = submitButton.text();
        
        // Show loading state
        submitButton.prop('disabled', true).text('Updating...');
        
        $.ajax({
            url: form.attr('action'),
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            headers: {
                'X-CSRFToken': form.find('[name=csrfmiddlewaretoken]').val(),
                'X-Requested-With': 'XMLHttpRequest'
            },
            success: function(response) {
                if (response.status === 'success') {
                    showNotification(response.message, 'success');
                    // Close the modal
                    modal.modal('hide');
                    // Reload the page to show the updated section
                    setTimeout(() => location.reload(), 1000);
                } else {
                    showNotification(response.message || 'Error updating section', 'error');
                    submitButton.prop('disabled', false).text(originalButtonText);
                }
            },
            error: function(xhr, status, error) {
                showNotification('Error updating section. Please try again.', 'error');
                submitButton.prop('disabled', false).text(originalButtonText);
                console.error('Error updating section:', error);
            }
        });
    });
    
    // Handle section deletion via AJAX
    $('[id^="deleteSectionModal"] form').on('submit', function(e) {
        e.preventDefault();
        
        const form = $(this);
        const modalId = form.closest('.modal').attr('id');
        const modal = $('#' + modalId);
        const submitButton = form.find('button[type="submit"]');
        const originalButtonText = submitButton.text();
        const sectionCard = $(`[data-section-id=${form.closest('.modal').attr('id').replace('deleteSectionModal', '')}]`);
        
        // Show loading state
        submitButton.prop('disabled', true).text('Deleting...');
        
        $.ajax({
            url: form.attr('action'),
            method: 'POST',
            data: form.serialize(),
            headers: {
                'X-CSRFToken': form.find('[name=csrfmiddlewaretoken]').val(),
                'X-Requested-With': 'XMLHttpRequest'
            },
            success: function(response) {
                if (response.status === 'success') {
                    showNotification(response.message, 'success');
                    // Close the modal
                    modal.modal('hide');
                    // Remove the section card from the DOM instead of reloading
                    sectionCard.fadeOut(500, function() {
                        $(this).remove();
                    });
                } else {
                    showNotification(response.message || 'Error deleting section', 'error');
                    submitButton.prop('disabled', false).text(originalButtonText);
                }
            },
            error: function(xhr, status, error) {
                showNotification('Error deleting section. Please try again.', 'error');
                submitButton.prop('disabled', false).text(originalButtonText);
                console.error('Error deleting section:', error);
            }
        });
    });
    
    // Handle lesson creation via AJAX
    $('[id^="createLessonModal"] form').on('submit', function(e) {
        e.preventDefault();
        
        const form = $(this);
        const formData = new FormData(form[0]);
        const modalId = form.closest('.modal').attr('id');
        const modal = $('#' + modalId);
        const submitButton = form.find('button[type="submit"]');
        const originalButtonText = submitButton.text();
        
        // Show loading state
        submitButton.prop('disabled', true).text('Creating...');
        
        $.ajax({
            url: form.attr('action'),
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            headers: {
                'X-CSRFToken': form.find('[name=csrfmiddlewaretoken]').val(),
                'X-Requested-With': 'XMLHttpRequest'
            },
            success: function(response) {
                if (response.status === 'success') {
                    showNotification(response.message, 'success');
                    // Close the modal
                    modal.modal('hide');
                    // Reset the form
                    form[0].reset();
                    // Reload the page to show the new lesson
                    setTimeout(() => location.reload(), 1000);
                } else {
                    showNotification(response.message || 'Error creating lesson', 'error');
                    submitButton.prop('disabled', false).text(originalButtonText);
                }
            },
            error: function(xhr, status, error) {
                showNotification('Error creating lesson. Please try again.', 'error');
                submitButton.prop('disabled', false).text(originalButtonText);
                console.error('Error creating lesson:', error);
            }
        });
    });
    
    // Handle lesson deletion via AJAX
    $('[id^="deleteLessonModal"] form').on('submit', function(e) {
        e.preventDefault();
        
        const form = $(this);
        const modalId = form.closest('.modal').attr('id');
        const modal = $('#' + modalId);
        const submitButton = form.find('button[type="submit"]');
        const originalButtonText = submitButton.text();
        const lessonItem = $(`[data-lesson-id=${form.closest('.modal').attr('id').replace('deleteLessonModal', '')}]`);
        
        // Show loading state
        submitButton.prop('disabled', true).text('Deleting...');
        
        $.ajax({
            url: form.attr('action'),
            method: 'POST',
            data: form.serialize(),
            headers: {
                'X-CSRFToken': form.find('[name=csrfmiddlewaretoken]').val(),
                'X-Requested-With': 'XMLHttpRequest'
            },
            success: function(response) {
                if (response.status === 'success') {
                    showNotification(response.message, 'success');
                    // Close the modal
                    modal.modal('hide');
                    // Remove the lesson item from the DOM instead of reloading
                    lessonItem.fadeOut(500, function() {
                        $(this).remove();
                    });
                } else {
                    showNotification(response.message || 'Error deleting lesson', 'error');
                    submitButton.prop('disabled', false).text(originalButtonText);
                }
            },
            error: function(xhr, status, error) {
                showNotification('Error deleting lesson. Please try again.', 'error');
                submitButton.prop('disabled', false).text(originalButtonText);
                console.error('Error deleting lesson:', error);
            }
        });
    });
});