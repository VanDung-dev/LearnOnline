/**
 * Sortable Utilities for Drag and Drop functionality
 * Provides reusable functions for jQuery UI sortable with AJAX save
 */
function initSortable(config) {
    const {
        containerSelector,
        itemSelector,
        itemDataAttr,
        getUrl,
        dataParam,
        messageSelector,
        messageText
    } = config;

    const container = $(containerSelector);

    if (container.length === 0) {
        return;
    }

    container.sortable({
        handle: '.handle',
        update: function(event, ui) {
            // Collect all item IDs in new order
            const itemIds = [];
            $(itemSelector).each(function() {
                itemIds.push($(this).data(itemDataAttr));
            });

            console.log(`Sending ${dataParam}:`, itemIds);

            // Get the AJAX URL
            const url = getUrl();
            console.log('URL:', url);

            // Show temporary saving message
            const messageElement = $(messageSelector);
            const originalText = messageText || messageElement.text();
            messageElement.text('Saving order...');

            // Prepare request data
            const requestData = {};
            requestData[dataParam] = itemIds;

            // Send AJAX request to update order
            $.ajax({
                url: url,
                method: 'POST',
                headers: {
                    'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val(),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                data: requestData,
                success: function(response) {
                    console.log('Server response:', response);
                    if (response.status === 'success') {
                        console.log('Items reordered successfully');
                        messageElement.text('Order saved successfully!');
                        setTimeout(function() {
                            messageElement.text(originalText);
                        }, 2000);
                    } else {
                        console.error('Error reordering items:', response.message);
                        messageElement.text('Error saving order: ' + response.message);
                        // Revert the sort
                        container.sortable('cancel');
                    }
                },
                error: function(xhr, status, error) {
                    console.error('AJAX error:', error);
                    console.error('Response text:', xhr.responseText);
                    messageElement.text('Error saving order. Check console for details.');
                    // Revert the sort
                    container.sortable('cancel');
                }
            });
        }
    });

    container.disableSelection();
}

// Initialize sortable for modules
function initModuleSortable(courseSlug) {
    initSortable({
        containerSelector: '.sortable-modules',
        itemSelector: '.sortable-module',
        itemDataAttr: 'module-id',
        getUrl: function() {
            return `/instructor/courses/${encodeURIComponent(courseSlug)}/reorder/`;
        },
        dataParam: 'module_order',
        messageSelector: '.text-muted:contains("Drag and drop modules")',
        messageText: null // Will use existing text
    });
}

// Initialize sortable for lessons within a module
function initLessonSortable(moduleId, courseSlug) {
    const container = $(`.sortable-lessons[data-module-id="${moduleId}"]`);
    const list = container.find('.lesson-list');

    if (list.length === 0) {
        return;
    }

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
                    } else {
                        console.error('Error reordering lessons:', response.message);
                    }
                },
                error: function(xhr, status, error) {
                    console.error('AJAX error:', error);
                    console.error('Response text:', xhr.responseText);
                }
            });
        }
    });

    list.disableSelection();
}

// Initialize sortable for quiz questions
function initQuestionSortable(params) {
    const { courseSlug, moduleId, lessonId, quizId } = params;

    initSortable({
        containerSelector: '.sortable-questions',
        itemSelector: '.sortable-question',
        itemDataAttr: 'question-id',
        getUrl: function() {
            return `/courses/${encodeURIComponent(courseSlug)}/modules/${moduleId}/lessons/${lessonId}/quiz/reorder/`;
        },
        dataParam: 'question_order',
        messageSelector: '.text-muted:contains("Drag and drop questions")',
        messageText: null // Will use existing text
    });
}

// Initialize all lesson sortables on the page
function initAllLessonSortables(courseSlug) {
    $('.sortable-lessons').each(function() {
        const moduleId = $(this).data('module-id');
        initLessonSortable(moduleId, courseSlug);
    });
}
