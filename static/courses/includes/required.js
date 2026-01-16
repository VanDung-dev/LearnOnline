function validateRequiredCourseForm(event) {
    const form = event.target.form || event.target.closest('form');

    // Get form fields
    const title = form.querySelector('#id_title');
    const shortDescription = form.querySelector('#id_short_description');
    const category = form.querySelector('#id_category');
    const openingDate = form.querySelector('#id_opening_date');
    const closingDate = form.querySelector('#id_closing_date');
    const expirationDate = form.querySelector('#id_expiration_date');
    const price = form.querySelector('#id_price');
    const certificatePrice = form.querySelector('#id_certificate_price');
    const isActive = form.querySelector('#id_is_active');

    // Reset validation styles
    const fields = [title, shortDescription, category, openingDate, closingDate, expirationDate, price, certificatePrice];
    fields.forEach(field => {
        if (field) {
            field.classList.remove('is-invalid');
        }
    });

    let isValid = true;
    let errorMessage = '';

    // ALWAYS REQUIRED: Title and Category (Database constraints)
    if (!title || !title.value.trim()) {
        if (title) title.classList.add('is-invalid');
        isValid = false;
        errorMessage += 'Course title is required.<br>';
    }

    if (!category || !category.value) {
        if (category) category.classList.add('is-invalid');
        isValid = false;
        errorMessage += 'Category is required.<br>';
    }

    // CONDITIONAL VALIDATION: If Is Active is checked, enforce everything else
    if (isActive && isActive.checked) {

        if (!shortDescription || !shortDescription.value.trim()) {
            if (shortDescription) shortDescription.classList.add('is-invalid');
            isValid = false;
            errorMessage += 'Short description is required for active courses.<br>';
        }

        if (!openingDate || !openingDate.value) {
            if (openingDate) openingDate.classList.add('is-invalid');
            isValid = false;
            errorMessage += 'Opening date is required for active courses.<br>';
        }

        if (!closingDate || !closingDate.value) {
            if (closingDate) closingDate.classList.add('is-invalid');
            isValid = false;
            errorMessage += 'Closing date is required for active courses.<br>';
        }

        if (!expirationDate || !expirationDate.value) {
            if (expirationDate) expirationDate.classList.add('is-invalid');
            isValid = false;
            errorMessage += 'Expiration date is required for active courses.<br>';
        }

        // Validate price fields
        const priceValue = price ? parseFloat(price.value) : NaN;
        const certificatePriceValue = certificatePrice ? parseFloat(certificatePrice.value) : NaN;

        if (isNaN(priceValue)) {
            if (price) price.classList.add('is-invalid');
            isValid = false;
            errorMessage += 'Course price is required.<br>';
        } else if (priceValue < 0) {
            if (price) price.classList.add('is-invalid');
            isValid = false;
            errorMessage += 'Course price cannot be negative.<br>';
        }

        if (isNaN(certificatePriceValue)) {
            if (certificatePrice) certificatePrice.classList.add('is-invalid');
            isValid = false;
            errorMessage += 'Certificate price is required.<br>';
        } else if (certificatePriceValue < 0) {
            if (certificatePrice) certificatePrice.classList.add('is-invalid');
            isValid = false;
            errorMessage += 'Certificate price cannot be negative.<br>';
        }

        // Check that both prices are notzero or non-zero at the same time
        if (!isNaN(priceValue) && !isNaN(certificatePriceValue)) {
            const bothZero = (priceValue === 0 && certificatePriceValue === 0);
            const bothNonZero = (priceValue > 0 && certificatePriceValue > 0);

            if (bothZero || bothNonZero) {
                if (price) price.classList.add('is-invalid');
                if (certificatePrice) certificatePrice.classList.add('is-invalid');
                isValid = false;
                if (bothZero) {
                    errorMessage += 'Please enter the course price OR the certificate price.<br>';
                } else if (bothNonZero) {
                    errorMessage += 'Only course prices OR certificate prices can be entered.<br>';
                }
            }
        }

        // Check date logic
        if (openingDate && closingDate && openingDate.value && closingDate.value) {
            const opening = new Date(openingDate.value);
            const closing = new Date(closingDate.value);
            if (opening >= closing) {
                closingDate.classList.add('is-invalid');
                isValid = false;
                errorMessage += 'Closing date must be after opening date.<br>';
            }
        }

        if (openingDate && expirationDate && openingDate.value && expirationDate.value) {
            const opening = new Date(openingDate.value);
            const expiration = new Date(expirationDate.value);
            if (opening >= expiration) {
                expirationDate.classList.add('is-invalid');
                isValid = false;
                errorMessage += 'Expiration date must be after opening date.<br>';
            }
        }

        if (closingDate && expirationDate && closingDate.value && expirationDate.value) {
            const closing = new Date(closingDate.value);
            const expiration = new Date(expirationDate.value);
            if (closing >= expiration) {
                expirationDate.classList.add('is-invalid');
                isValid = false;
                errorMessage += 'Expiration date must be after closing date.<br>';
            }
        }
    }

    if (!isValid) {
        event.preventDefault();
        showValidationModal(errorMessage);
        return false;
    }

    return true;
}

function showValidationModal(message) {
    const modalBody = document.querySelector('#validation-modal .modal-body');
    if (modalBody) {
        modalBody.innerHTML = message;
        const modal = new bootstrap.Modal(document.getElementById('validation-modal'));
        modal.show();
    }
}