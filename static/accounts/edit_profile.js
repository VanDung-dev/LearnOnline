document.addEventListener('DOMContentLoaded', function () {
    // Select the file input using the standard Django ID for profile_picture field
    const fileInput = document.getElementById('id_profile_picture');
    const previewImg = document.getElementById('profilePreview');
    const placeholder = document.getElementById('profilePlaceholder');

    if (fileInput) {
        fileInput.addEventListener('change', function (e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    previewImg.src = e.target.result;
                    previewImg.classList.remove('d-none');
                    if (placeholder) placeholder.classList.add('d-none');
                }
                reader.readAsDataURL(file);
            }
        });
    }

    // Add bootstrap form-control classes to inputs if they don't have them
    const inputs = document.querySelectorAll('input:not([type="checkbox"]):not([type="radio"]):not([type="file"]), textarea, select');
    inputs.forEach(input => {
        input.classList.add('form-control');
        if (!input.placeholder) input.placeholder = ' '; // Required for floating labels
    });
});
