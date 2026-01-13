document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('payment-form');
    const payButton = document.getElementById('pay-button');
    const overlay = document.getElementById('form-overlay');
    const errorSummary = document.getElementById('error-summary');
    const clientTokenInput = document.getElementById('client_token');

    // Fade-in payment logos when loaded (prevent flash)
    document.querySelectorAll('.payment-logo').forEach(img => {
        const showLogo = () => {
            img.style.opacity = '1';
            img.classList.add('loaded');
        };
        if (img.complete) {
            showLogo();
        } else {
            img.addEventListener('load', showLogo);
            img.addEventListener('error', showLogo);
        }
    });

    // body attribute for styling
    try {
        const purchaseType = document.querySelector('input[name="purchase_type"]').value;
        if (purchaseType) document.body.setAttribute('data-purchase-type', purchaseType);
    } catch (_) { }

    // Helpers
    function showOverlay(show) {
        if (!overlay) return;
        overlay.classList.toggle('d-none', !show);
    }

    function uuidv4() {
        // RFC4122-ish UUID v4 generator for client token
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
            const r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }

    // Ensure there is an idempotency token per form open
    try {
        if (clientTokenInput && !clientTokenInput.value) {
            clientTokenInput.value = uuidv4();
        }
    } catch (_) { }
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
        ['card_number', 'expiry_date', 'cvv'].forEach(id => setFieldError(id, ''));
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

    // Payment Method Selection
    const methodInput = document.getElementById('payment_method');
    const creditCardSection = document.getElementById('credit-card-section');
    const redirectSection = document.getElementById('redirect-section');
    const selectedMethodName = document.getElementById('selected-method-name');

    document.querySelectorAll('.method-option').forEach(option => {
        option.addEventListener('click', function () {
            // UI Update
            document.querySelectorAll('.method-option').forEach(opt => opt.classList.remove('selected', 'border-primary', 'bg-light'));
            this.classList.add('selected', 'border-primary', 'bg-light');

            const method = this.getAttribute('data-method');
            methodInput.value = method;

            if (method === 'visa' || method === 'mastercard') {
                // Set card type for backend validation
                document.getElementById('card_type').value = method;
                creditCardSection.classList.remove('d-none');
                redirectSection.classList.add('d-none');
            } else {
                creditCardSection.classList.add('d-none');
                redirectSection.classList.remove('d-none');

                // Update redirect message name
                const methodNameMap = {
                    'momo': 'MoMo Wallet',
                    'zalopay': 'ZaloPay',
                    'local_bank': 'Local Bank App',
                    'paypal': 'PayPal'
                };
                if (selectedMethodName) selectedMethodName.textContent = methodNameMap[method] || method;
            }
            clearErrors();
            validateForm();
        });
    });

    // Removed old card-option click handlers as they are no longer in the DOM

    // Masking and validation
    const cardNumber = document.getElementById('card_number');
    const expiry = document.getElementById('expiry_date');
    const cvv = document.getElementById('cvv');

    function onlyDigits(str) { return (str || '').replace(/\D+/g, ''); }

    // Luhn algorithm to validate card numbers
    function luhnCheck(cardNumber) {
        const digits = onlyDigits(cardNumber);
        if (digits.length < 13) return false;
        let sum = 0;
        let isEven = false;
        for (let i = digits.length - 1; i >= 0; i--) {
            let digit = parseInt(digits[i], 10);
            if (isEven) {
                digit *= 2;
                if (digit > 9) digit -= 9;
            }
            sum += digit;
            isEven = !isEven;
        }
        return sum % 10 === 0;
    }

    // Detect card type from BIN (Bank Identification Number)
    function detectCardType(cardNumber) {
        const digits = onlyDigits(cardNumber);
        if (digits.length < 1) return null;
        // Visa: starts with 4
        if (/^4/.test(digits)) return 'visa';
        // Mastercard: 51-55 or 2221-2720
        const prefix2 = parseInt(digits.substring(0, 2), 10) || 0;
        const prefix4 = parseInt(digits.substring(0, 4), 10) || 0;
        if ((prefix2 >= 51 && prefix2 <= 55) || (prefix4 >= 2221 && prefix4 <= 2720)) {
            return 'mastercard';
        }
        return null;
    }

    function formatCardNumber(value) {
        const digits = onlyDigits(value).slice(0, 19);
        return digits.replace(/(.{4})/g, '$1 ').trim();
    }
    function validateCardNumber(value) {
        const digits = onlyDigits(value);
        if (digits.length < 13 || digits.length > 19) return false;
        return luhnCheck(digits);
    }
    function formatExpiry(value) {
        const digits = onlyDigits(value).slice(0, 4);
        if (digits.length <= 2) return digits;
        return digits.slice(0, 2) + '/' + digits.slice(2);
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
        if (creditCardSection && !creditCardSection.classList.contains('d-none')) {
            if (!document.getElementById('card_type').value) {
                setCardTypeError('Please select a card type.');
                valid = false;
            }
            if (!validateCardNumber(cardNumber.value)) {
                setFieldError('card_number', 'Enter a valid card number.');
                valid = false;
            }
            // Validate cardholder name
            const cardholderName = document.getElementById('cardholder_name');
            if (cardholderName && (!cardholderName.value || cardholderName.value.trim().length < 2)) {
                setFieldError('cardholder_name', 'Enter the cardholder name.');
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

            // Billing validation
            const billingAddress = document.getElementById('billing_address');
            if (billingAddress && !billingAddress.value.trim()) {
                setFieldError('billing_address', 'Please enter your billing address.');
                valid = false;
            }
            const zipCode = document.getElementById('zip_code');
            if (zipCode && !zipCode.value.trim()) {
                setFieldError('zip_code', 'Zip code required.');
                valid = false;
            }
        }
        payButton.disabled = !valid;
        return valid;
    }

    if (cardNumber) {
        cardNumber.addEventListener('input', (e) => {
            const pos = e.target.selectionStart;
            e.target.value = formatCardNumber(e.target.value);

            // Auto-detect card type from BIN
            const detected = detectCardType(e.target.value);
            if (detected && (detected === 'visa' || detected === 'mastercard')) {
                // Auto-select the detected card type
                const currentMethod = methodInput.value;
                if (currentMethod !== detected) {
                    methodInput.value = detected;
                    document.getElementById('card_type').value = detected;
                    // Update UI selection
                    document.querySelectorAll('.method-option').forEach(opt => {
                        const method = opt.getAttribute('data-method');
                        if (method === detected) {
                            opt.classList.add('selected', 'border-primary', 'bg-light');
                        } else if (method === 'visa' || method === 'mastercard') {
                            opt.classList.remove('selected', 'border-primary', 'bg-light');
                        }
                    });
                }
            }
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
            e.target.value = onlyDigits(e.target.value).slice(0, 4);
            validateForm();
        });
    }

    form.addEventListener('submit', function (e) {
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

    // Billing inputs listeners
    ['billing_address', 'zip_code', 'phone_number'].forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener('input', validateForm);
        }
    });

    // Initial state
    validateForm();
});