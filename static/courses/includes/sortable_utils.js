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
        update: function (event, ui) {
            // Collect all item IDs in new order
            const itemIds = [];
            $(itemSelector).each(function () {
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
                success: function (response) {
                    console.log('Server response:', response);
                    if (response.status === 'success') {
                        console.log('Items reordered successfully');
                        messageElement.text('Order saved successfully!');
                        setTimeout(function () {
                            messageElement.text(originalText);
                        }, 2000);
                    } else {
                        console.error('Error reordering items:', response.message);
                        messageElement.text('Error saving order: ' + response.message);
                        // Revert the sort
                        container.sortable('cancel');
                    }
                },
                error: function (xhr, status, error) {
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

// Initialize sortable for sections
function initSectionSortable(courseSlug) {
    initSortable({
        containerSelector: '.sortable-sections',
        itemSelector: '.sortable-section',
        itemDataAttr: 'section-id',
        getUrl: function () {
            return `/dashboard/courses/${encodeURIComponent(courseSlug)}/reorder/`;
        },
        dataParam: 'section_order',
        messageSelector: '.text-muted:contains("Drag and drop sections")',
        messageText: null // Will use existing text
    });
}

// Initialize sortable for subsections within a section
function initSubsectionSortable(sectionId, courseSlug) {
    initSortable({
        containerSelector: `.sortable-subsections[data-section-id="${sectionId}"]`,
        itemSelector: '.sortable-subsection',
        itemDataAttr: 'subsection-id',
        getUrl: function () {
            return `/dashboard/courses/${encodeURIComponent(courseSlug)}/sections/${sectionId}/subsections/reorder/`;
        },
        dataParam: 'subsection_order',
        messageSelector: '.text-muted:contains("Drag and drop subsections")',
        messageText: null
    });
}

// Initialize sortable for lessons within a section or subsection
function initLessonSortable(sectionId, courseSlug, subsectionId = null) {
    let containerSelector;
    if (subsectionId) {
        containerSelector = `.sortable-lessons[data-subsection-id="${subsectionId}"]`;
    } else {
        containerSelector = `.sortable-lessons[data-section-id="${sectionId}"]`;
    }

    const container = $(containerSelector);
    const list = container.find('.lesson-list');

    if (list.length === 0) {
        // Try direct list if container IS the list or structured differently
        // But based on edit_course.html, .sortable-lessons contains .lesson-list ul.
        // Wait, legacy: <div class="sortable-lessons" ...> <ul class="lesson-list"> 
        // Subsection: <ul class="list-group ... sortable-lessons" ...> 
        // In subsection, the UL itself has class sortable-lessons.
        // So container IS the list if it is UL.
        if (container.is('ul')) {
            // container is the list, but initSortable logic below uses 'list' var.
            // We can just reassign list = container.
        }
    }

    // Let's refine selection logic
    let $sortableList = container.find('.lesson-list');

    if ($sortableList.length === 0) {
        // If no internal .lesson-list found, the container itself is the list (whether ul or div)
        // This supports the new card-based layout which uses a div container directly
        $sortableList = container;
    }

    if ($sortableList.length === 0) {
        return;
    }

    $sortableList.sortable({
        handle: '.handle',
        update: function (event, ui) {
            const lessonIds = [];
            $sortableList.find('.sortable-lesson').each(function () {
                lessonIds.push($(this).data('lesson-id'));
            });

            console.log('Sending lesson order:', lessonIds);

            let url;
            if (subsectionId) {
                url = `/dashboard/courses/${encodeURIComponent(courseSlug)}/sections/${sectionId}/subsections/${subsectionId}/lessons/reorder/`;
            } else {
                url = `/dashboard/courses/${encodeURIComponent(courseSlug)}/sections/${sectionId}/lessons/reorder/`;
            }

            $.ajax({
                url: url,
                method: 'POST',
                headers: {
                    'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val(),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                data: {
                    lesson_order: lessonIds
                },
                success: function (response) {
                    console.log('Server response:', response);
                    if (response.status === 'success') {
                        console.log('Lessons reordered successfully');
                    } else {
                        console.error('Error reordering lessons:', response.message);
                    }
                },
                error: function (xhr, status, error) {
                    console.error('AJAX error:', error);
                    console.error('Response text:', xhr.responseText);
                }
            });
        }
    });

    $sortableList.disableSelection();
}

// Initialize sortable for quiz questions
function initQuestionSortable(params) {
    const { courseSlug, sectionId, lessonId, quizId } = params;

    initSortable({
        containerSelector: '.sortable-questions',
        itemSelector: '.sortable-question',
        itemDataAttr: 'question-id',
        getUrl: function () {
            return `/courses/${encodeURIComponent(courseSlug)}/sections/${sectionId}/lessons/${lessonId}/quiz/reorder/`;
        },
        dataParam: 'question_order',
        messageSelector: '.text-muted:contains("Drag and drop questions")',
        messageText: null // Will use existing text
    });
}

// Initialize all lesson sortables on the page
function initAllLessonSortables(courseSlug) {
    $('.sortable-lessons').each(function () {
        const container = $(this);
        const sectionId = container.data('section-id') || container.closest('[data-section-id]').data('section-id');
        const subsectionId = container.data('subsection-id');

        // Ensure we have sectionId. For legacy lessons in section, it's on container.
        // For subsection lessons, it might be on container (if I added it) or invalid.
        // I added data-section-id to subsection loop? No I didn't yet.
        // But I can find closest section container.
        // The .sortable-subsections div has data-section-id.

        if (sectionId) {
            initLessonSortable(sectionId, courseSlug, subsectionId);
        }
    });

    // Also initialize subsection sortables
    $('.sortable-subsections').each(function () {
        const sectionId = $(this).data('section-id');
        if (sectionId) {
            initSubsectionSortable(sectionId, courseSlug);
        }
    });
}
