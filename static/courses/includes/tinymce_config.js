/**
 * Shared TinyMCE configuration for LearnOnline
 */

// Get CSRF token function
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Shared TinyMCE configuration
const sharedTinyMCEConfig = {
    plugins: 'lists link image table code help wordcount',
    toolbar: 'undo redo | styles | bold italic underline strikethrough | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image | help',
    menubar: false,
    statusbar: false,
    branding: false,
    promotion: false,
    image_advtab: true,
    image_caption: true,
    images_upload_url: '/courses/upload_image/',
    toolbar_mode: 'floating',
    setup: function(editor) {
        editor.on('init', function() {
            // Ensure the editor container has the correct height
            const container = editor.getContainer();
            const iframe = container.querySelector('iframe');
            if (iframe) {
                iframe.style.height = '500px';
            }
        });
    },
    images_upload_handler: function (blobInfo, progress) {
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            xhr.withCredentials = false;
            xhr.open('POST', '/courses/upload_image/');

            // Add CSRF token
            const csrftoken = getCookie('csrftoken');
            xhr.setRequestHeader("X-CSRFToken", csrftoken);

            xhr.upload.onprogress = function (e) {
                progress(e.loaded / e.total * 100);
            };

            xhr.onload = function() {
                if (xhr.status !== 200) {
                    reject('HTTP Error: ' + xhr.status);
                    return;
                }

                try {
                    const json = JSON.parse(xhr.responseText);

                    if (!json || typeof json.location != 'string') {
                        reject('Invalid JSON: ' + xhr.responseText);
                        return;
                    }

                    resolve(json.location);
                } catch (e) {
                    reject('Error parsing response: ' + e.message);
                }
            };

            xhr.onerror = function() {
                reject('Network error occurred');
            };

            const formData = new FormData();
            formData.append('file', blobInfo.blob(), blobInfo.filename());

            xhr.send(formData);
        });
    }
};

// Function to initialize TinyMCE with shared configuration
function initSharedTinyMCE(selector, height = 1000) {
    if (typeof tinymce !== 'undefined') {
        const config = {...sharedTinyMCEConfig};
        config.selector = selector;
        config.height = height;
        
        // Update the iframe height in setup function
        config.setup = function(editor) {
            editor.on('init', function() {
                const container = editor.getContainer();
                const iframe = container.querySelector('iframe');
                if (iframe) {
                    iframe.style.height = height + 'px';
                }
            });
        };
        
        return tinymce.init(config);
    }
}

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { initSharedTinyMCE, sharedTinyMCEConfig, getCookie };
}