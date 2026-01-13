document.addEventListener('DOMContentLoaded', function () {
    // Toggle password visibility
    document.querySelectorAll('.toggle-password').forEach(function (button) {
        button.addEventListener('click', function () {
            const targetId = this.getAttribute('data-target');
            const passwordInput = document.getElementById(targetId);
            const icon = this.querySelector('i');

            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                icon.classList.remove('bi-eye-slash');
                icon.classList.add('bi-eye');
            } else {
                passwordInput.type = 'password';
                icon.classList.remove('bi-eye');
                icon.classList.add('bi-eye-slash');
            }
        });
    });

    // Forgot Password Logic - Refactored for Robustness
    console.log('Login JS: Initializing Forgot Password Logic');

    function showMessage(msg, type) {
        const messageDiv = document.getElementById('forgotPasswordMessage');
        if (messageDiv) {
            messageDiv.className = `alert alert-${type}`;
            messageDiv.innerHTML = msg;
            messageDiv.classList.remove('d-none');
        } else {
            console.error('Login JS: Message div not found', msg);
        }
    }

    function isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    function initiateRecovery() {
        console.log('Login JS: Initiating recovery...');
        const sendBtn = document.getElementById('sendRecoveryEmail');
        const emailInput = document.getElementById('recoveryEmail');

        if (!sendBtn || !emailInput) {
            console.error('Login JS: Elements missing', { sendBtn, emailInput });
            return;
        }

        const email = emailInput.value.trim();

        // Basic validation
        if (!email) {
            showMessage('Please enter your email address.', 'danger');
            return;
        }
        if (!isValidEmail(email)) {
            showMessage('Please enter a valid email address.', 'danger');
            return;
        }

        // Simulate API call/processing
        sendBtn.disabled = true;
        const originalText = sendBtn.innerHTML;
        sendBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Sending...';

        setTimeout(function () {
            // Success simulation
            showMessage(`We have sent a password recovery link to <strong>${email}</strong>. Please check your inbox (and spam folder).`, 'success');
            sendBtn.innerHTML = 'Sent!';

            // Reset after a delay or keep it as is
            setTimeout(() => {
                sendBtn.disabled = false;
                sendBtn.innerHTML = originalText;
            }, 3000);

        }, 1000);
    }

    // Event Delegation for Button Click (Safer than direct attachment if timing is off)
    document.body.addEventListener('click', function (e) {
        if (e.target && e.target.id === 'sendRecoveryEmail') {
            e.preventDefault();
            initiateRecovery();
        }
    });

    // Form Submit Handler
    const forgotForm = document.getElementById('forgotPasswordForm');
    if (forgotForm) {
        forgotForm.addEventListener('submit', function (e) {
            e.preventDefault();
            initiateRecovery();
        });
    }

    // Clear message when modal is opened/closed
    const modalEl = document.getElementById('forgotPasswordModal');
    if (modalEl) {
        modalEl.addEventListener('hidden.bs.modal', function () {
            const messageDiv = document.getElementById('forgotPasswordMessage');
            const emailInput = document.getElementById('recoveryEmail');
            const sendBtn = document.getElementById('sendRecoveryEmail');

            if (messageDiv) messageDiv.classList.add('d-none');
            if (emailInput) emailInput.value = '';

            // Reset button if closed in 'Sent' state
            if (sendBtn && sendBtn.innerText === 'Sent!') {
                sendBtn.innerHTML = 'Send Recovery Link';
                sendBtn.disabled = false;
            }
        });
    }
});