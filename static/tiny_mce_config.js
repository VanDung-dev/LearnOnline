document.addEventListener("DOMContentLoaded", function () {
    // Helper for CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const commonConfig = {
        height: 200,
        menubar: false,
        statusbar: true,
        resize: true,
        plugins: [
            'advlist', 'autolink', 'lists', 'link', 'image', 'charmap', 'preview',
            'anchor', 'searchreplace', 'visualblocks', 'code', 'fullscreen',
            'insertdatetime', 'media', 'table', 'help', 'wordcount'
        ],
        toolbar: 'undo redo | blocks | ' +
            'bold italic backcolor | alignleft aligncenter ' +
            'alignright alignjustify | bullist numlist outdent indent | ' +
            'link image | removeformat | help',
        setup: function (editor) {
            editor.on('change', function () {
                editor.save();
            });
        },
        content_style: 'body { font-family:Helvetica,Arial,sans-serif; font-size:14px }',
        images_upload_url: '/courses/upload_image/',
        images_upload_handler: function (blobInfo, progress) {
            return new Promise((resolve, reject) => {
                const xhr = new XMLHttpRequest();
                xhr.withCredentials = false;
                xhr.open('POST', '/courses/upload_image/');

                const csrftoken = getCookie('csrftoken');
                xhr.setRequestHeader("X-CSRFToken", csrftoken);

                xhr.upload.onprogress = function (e) {
                    progress(e.loaded / e.total * 100);
                };

                xhr.onload = function () {
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

                xhr.onerror = function () {
                    reject('Network error occurred');
                };

                const formData = new FormData();
                formData.append('file', blobInfo.blob(), blobInfo.filename());
                xhr.send(formData);
            });
        }
    };

    // Auto init for .tinymce-editor
    if (document.querySelector('.tinymce-editor')) {
        // Check if tinymce is defined to avoid errors on pages without the script
        if (typeof tinymce !== 'undefined') {
            tinymce.init({
                ...commonConfig,
                selector: '.tinymce-editor'
            });
        }
    }

    // Expose config for other pages to use specific selectors
    window.tinyMceConfig = commonConfig;
});
