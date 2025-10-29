document.addEventListener('DOMContentLoaded', function() {
    // Toggle password visibility
    document.querySelectorAll('.toggle-password').forEach(function(button) {
        button.addEventListener('click', function() {
            // Get the target and confirm password fields
            const targetId = this.getAttribute('data-target');
            const confirmId = this.getAttribute('data-confirm');
            
            const targetInput = document.getElementById(targetId);
            const confirmInput = document.getElementById(confirmId);
            
            // Get icons for both buttons
            const targetIcon = this.querySelector('i');
            const confirmButton = document.querySelector(`[data-target="${confirmId}"]`);
            const confirmIcon = confirmButton.querySelector('i');
            
            // Toggle password visibility for both fields
            if (targetInput.type === 'password') {
                targetInput.type = 'text';
                confirmInput.type = 'text';
                targetIcon.classList.remove('bi-eye-slash');
                targetIcon.classList.add('bi-eye');
                confirmIcon.classList.remove('bi-eye-slash');
                confirmIcon.classList.add('bi-eye');
            } else {
                targetInput.type = 'password';
                confirmInput.type = 'password';
                targetIcon.classList.remove('bi-eye');
                targetIcon.classList.add('bi-eye-slash');
                confirmIcon.classList.remove('bi-eye');
                confirmIcon.classList.add('bi-eye-slash');
            }
        });
    });
});