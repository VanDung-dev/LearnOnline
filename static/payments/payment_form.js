document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('payment-form');
    const payButton = document.getElementById('pay-button');
    const overlay = document.getElementById('form-overlay');
    const errorSummary = document.getElementById('error-summary');

    // body attribute for styling
    try {
        const purchaseType = document.querySelector('input[name="purchase_type"]').value;
        if (purchaseType) document.body.setAttribute('data-purchase-type', purchaseType);
    } catch (_) {}

    // Helpers
    function showOverlay(show) {
        if (!overlay) return;
        overlay.classList.toggle('d-none', !show);
    }
    function setFieldError(id, message) {
        const input = document.getElementById(id);
        const feedback = document.getElementById(id + '_error');
        if (feedback) feedback.textContent = message || '';
        if (input) input.classList.toggle('is-invalid', !!message);
    }
    function setCardTypeError(message) {
        const el = document.getElementById('card_type_error');
        if (el) el.classList.toggle('d-none', !message);
        if (el) el.textContent = message || '';
        // highlight card options
        document.querySelectorAll('.card-option').forEach(opt => {
            opt.classList.toggle('is-invalid', !!message);
        });
    }
    function clearErrors() {
        ['card_number','expiry_date','cvv'].forEach(id => setFieldError(id, ''));
        setCardTypeError('');
        if (errorSummary) {
            errorSummary.classList.add('d-none');
            errorSummary.textContent = '';
        }
    }
    function showErrorSummary(messages) {
        if (!errorSummary) return;
        errorSummary.innerHTML = Array.isArray(messages) ? messages.map(m => `<div>${m}</div>`).join('') : (messages || '');
        errorSummary.classList.remove('d-none');
    }

    // Card type selection visual feedback
    document.querySelectorAll('.card-option').forEach(option => {
        option.addEventListener('click', function() {
            document.querySelectorAll('.card-option').forEach(opt => {
                opt.classList.remove('selected');
            });
            this.classList.add('selected');
            document.getElementById('card_type').value = this.getAttribute('data-card-type');
            setCardTypeError('');
            validateForm();
        });
    });

    // Masking and validation
    const cardNumber = document.getElementById('card_number');
    const expiry = document.getElementById('expiry_date');
    const cvv = document.getElementById('cvv');

    function onlyDigits(str) { return (str || '').replace(/\D+/g, ''); }

    function formatCardNumber(value) {
        const digits = onlyDigits(value).slice(0, 19);
        return digits.replace(/(.{4})/g, '$1 ').trim();
    }
    function validateCardNumber(value) {
        const digits = onlyDigits(value);
        return digits.length >= 13 && digits.length <= 19;
    }
    function formatExpiry(value) {
        const digits = onlyDigits(value).slice(0, 4);
        if (digits.length <= 2) return digits;
        return digits.slice(0,2) + '/' + digits.slice(2);
    }
    function validateExpiry(value) {
        const match = /^(\d{2})\/(\d{2})$/.exec(value || '');
        if (!match) return false;
        const mm = parseInt(match[1], 10);
        const yy = parseInt(match[2], 10);
        if (mm < 1 || mm > 12) return false;
        // assume 20xx
        const now = new Date();
        const currentYY = now.getFullYear() % 100;
        const currentMM = now.getMonth() + 1;
        if (yy < currentYY) return false;
        if (yy === currentYY && mm < currentMM) return false;
        return true;
    }
    function validateCVV(value) {
        const digits = onlyDigits(value);
        return digits.length >= 3 && digits.length <= 4;
    }

    function validateForm() {
        let valid = true;
        clearErrors();
        if (!document.getElementById('card_type').value) {
            setCardTypeError('Please select a card type.');
            valid = false;
        }
        if (!validateCardNumber(cardNumber.value)) {
            setFieldError('card_number', 'Enter a valid card number.');
            valid = false;
        }
        if (!validateExpiry(expiry.value)) {
            setFieldError('expiry_date', 'Enter a valid expiry in MM/YY.');
            valid = false;
        }
        if (!validateCVV(cvv.value)) {
            setFieldError('cvv', 'Enter a valid CVV (3–4 digits).');
            valid = false;
        }
        payButton.disabled = !valid;
        return valid;
    }

    if (cardNumber) {
        cardNumber.addEventListener('input', (e) => {
            const pos = e.target.selectionStart;
            e.target.value = formatCardNumber(e.target.value);
            validateForm();
        });
    }
    if (expiry) {
        expiry.addEventListener('input', (e) => {
            e.target.value = formatExpiry(e.target.value);
            validateForm();
        });
    }
    if (cvv) {
        cvv.addEventListener('input', (e) => {
            e.target.value = onlyDigits(e.target.value).slice(0,4);
            validateForm();
        });
    }

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        if (!validateForm()) {
            showErrorSummary('Please correct the highlighted errors and try again.');
            return;
        }
        clearErrors();
        const originalText = payButton.innerHTML;
        payButton.disabled = true;
        payButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Processing...';
        showOverlay(true);

        const formData = new FormData(this);
        fetch(processPaymentUrl, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.href = data.redirect_url;
            } else {
                const messages = [];
                if (data.message) messages.push(data.message);
                if (data.errors) {
                    Object.entries(data.errors).forEach(([field, msgs]) => {
                        if (field === 'card_type') setCardTypeError((msgs || []).join(' '));
                        else setFieldError(field, (msgs || []).join(' '));
                    });
                }
                showErrorSummary(messages.length ? messages : ['Payment failed.']);
                payButton.disabled = false;
                payButton.innerHTML = originalText;
                showOverlay(false);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showErrorSummary('An error occurred during payment processing. Please try again.');
            payButton.disabled = false;
            payButton.innerHTML = originalText;
            showOverlay(false);
        });
    });

    // Initial state
    validateForm();
});