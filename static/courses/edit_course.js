$(document).ready(function () {
    // Initialize TinyMCE for course description
    // Handled by base.html via .tinymce-editor class or inline script

    // Ensure TinyMCE content is synced before form submission
    const courseForm = document.getElementById('course-edit-form');
    if (courseForm) {
        courseForm.addEventListener('submit', function (e) {
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

    // Initialize sortable for sections
    const courseSlug = $('.sortable-sections').data('course-slug');
    if (courseSlug) {
        initSectionSortable(courseSlug);

        // Initialize sortable for all lessons
        initAllLessonSortables(courseSlug);
    }

    // Handle lesson type changes in create lesson modals
    $('select[id^="lesson_type_"]').each(function () {
        const sectionId = $(this).attr('id').split('_').pop();
        const textSection = $(`#text-content-section-${sectionId}`);
        const videoSection = $(`#video-content-section-${sectionId}`);
        const quizSection = $(`#quiz-content-section-${sectionId}`);

        $(this).on('change', function () {
            // Hide all sections
            textSection.hide();
            videoSection.hide();
            quizSection.hide();

            // Show the relevant section based on selection
            switch ($(this).val()) {
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

    // ---------------------------------------------------------
    // Price & Certificate Price Mutual Exclusivity Logic
    // ---------------------------------------------------------
    const $priceInput = $('#id_price');
    const $certPriceInput = $('#id_certificate_price');
    let unlockTimeout = null;

    function setLocked($input, isLocked) {
        if (isLocked) {
            // Use a darker gray for better visibility (#d1d5db which is darker than standard disabled)
            $input.prop('readonly', true).css('background-color', '#d1d5db').addClass('text-muted');
            $input.removeClass('bg-light');
        } else {
            $input.prop('readonly', false).css('background-color', '').removeClass('text-muted');
        }
    }

    function handlePriceExclusivity($active, $passive) {
        // On Focus: Lock the other immediately
        $active.on('focus', function () {
            // If I am already locked/readonly, do not attempt to lock the other.
            // This prevents a deadlock where clicking a locked field locks the active field.
            if ($(this).prop('readonly')) {
                return;
            }

            // Cancel any pending unlock to avoid weird race conditions
            if (unlockTimeout) {
                clearTimeout(unlockTimeout);
                unlockTimeout = null;
            }
            setLocked($passive, true);
        });

        // On Blur: If value is 0 or invalid, unlock the other immediately
        // This ensures if user just clicks in and leaves without typing, we don't leave the other locked.
        $active.on('blur', function () {
            // If I am locked, I shouldn't affect state
            if ($(this).prop('readonly')) {
                return;
            }

            const val = parseFloat($(this).val());
            if (isNaN(val) || val === 0) {
                if (unlockTimeout) {
                    clearTimeout(unlockTimeout);
                    unlockTimeout = null;
                }
                setLocked($passive, false);
            }
        });

        // On Input: Check value
        $active.on('input', function () {
            // If locked, ignore
            if ($(this).prop('readonly')) {
                return;
            }

            const val = parseFloat($(this).val());

            // If value > 0, ensure the other is locked
            if (val > 0) {
                if (unlockTimeout) {
                    clearTimeout(unlockTimeout);
                    unlockTimeout = null;
                }
                setLocked($passive, true);
            }
            // If value is 0 (or invalid/empty treated as 0 intention), wait 1s then unlock
            else {
                if (unlockTimeout) {
                    clearTimeout(unlockTimeout);
                }

                unlockTimeout = setTimeout(function () {
                    // Double check value in case it changed rapidly
                    const currentVal = parseFloat($active.val());
                    if (isNaN(currentVal) || currentVal === 0) {
                        setLocked($passive, false);
                    }
                }, 1000);
            }
        });
    }

    // Apply logic to both
    handlePriceExclusivity($priceInput, $certPriceInput);
    handlePriceExclusivity($certPriceInput, $priceInput);

    // Initial State Check on Page Load
    const initPrice = parseFloat($priceInput.val());
    const initCertPrice = parseFloat($certPriceInput.val());

    if (initPrice > 0) {
        setLocked($certPriceInput, true);
    } else if (initCertPrice > 0) {
        setLocked($priceInput, true);
    }


});
