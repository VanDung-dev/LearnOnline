$(document).ready(function() {
    // Make category dropdown searchable
    const categorySelect = $('#id_category');

    // Initialize Select2 only if the element exists
    if (categorySelect.length > 0) {
        // Check if Select2 is loaded
        if ($.fn.select2) {
            categorySelect.select2({
                placeholder: "Search or select a category",
                allowClear: true,
                width: '100%'
            });
        }
    }

    // Open add category modal
    $('#add-category-btn').on('click', function() {
        $('#addCategoryModal').modal('show');
    });

    // Save new category
    $('#saveCategoryBtn').on('click', function() {
        const categoryName = $('#categoryName').val().trim();
        const categoryDescription = $('#categoryDescription').val().trim();
        const saveBtn = $(this);
        const originalText = saveBtn.text();
        
        // Validate category name
        if (!categoryName) {
            $('#categoryName').addClass('is-invalid');
            return;
        } else {
            $('#categoryName').removeClass('is-invalid');
        }
        
        // Show loading state
        saveBtn.prop('disabled', true).text('Saving...');

        // Send AJAX request to create new category
        $.ajax({
            url: '/instructor/courses/create-category-ajax/',
            method: 'POST',
            data: {
                'name': categoryName,
                'description': categoryDescription,
                'csrfmiddlewaretoken': $('[name=csrfmiddlewaretoken]').val()
            },
            success: function(response) {
                if (response.status === 'success') {
                    // Add new option to category select
                    const newOption = new Option(response.name, response.id, true, true);
                    categorySelect.append(newOption).trigger('change');
                    
                    // Close modal and reset form
                    $('#addCategoryModal').modal('hide');
                    $('#addCategoryForm')[0].reset();
                    
                    // Show success message
                    const alertHtml = `
                        <div class="alert alert-success alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3" 
                             style="z-index: 9999;" role="alert">
                            Category "${response.name}" created successfully!
                            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                        </div>
                    `;
                    $('body').append(alertHtml);
                    setTimeout(() => $('.alert').fadeOut(() => $('.alert').remove()), 3000);
                } else {
                    // Show error message
                    const alertHtml = `
                        <div class="alert alert-danger alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3" 
                             style="z-index: 9999;" role="alert">
                            Error creating category: ${response.message}
                            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                        </div>
                    `;
                    $('body').append(alertHtml);
                    setTimeout(() => $('.alert').fadeOut(() => $('.alert').remove()), 3000);
                }
            },
            error: function(xhr, status, error) {
                console.log('AJAX Error:', xhr, status, error);
                // Show error message
                const alertHtml = `
                    <div class="alert alert-danger alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3" 
                         style="z-index: 9999;" role="alert">
                        Error creating category. Please try again.
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>
                `;
                $('body').append(alertHtml);
                setTimeout(() => $('.alert').fadeOut(() => $('.alert').remove()), 3000);
            },
            complete: function() {
                // Restore button state
                saveBtn.prop('disabled', false).text(originalText);
            }
        });
    });
});