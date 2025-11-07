document.addEventListener('DOMContentLoaded', function() {
    const loadingBar = document.getElementById('loading-bar');

    // Show loading bar on page load
    loadingBar.classList.add('loading');

    // Complete loading bar when page is fully loaded
    window.addEventListener('load', function() {
        loadingBar.classList.remove('loading');
        loadingBar.classList.add('complete');

        // Hide the loading bar after animation completes
        setTimeout(function() {
            loadingBar.style.transform = 'scaleX(0)';
        }, 300);
    });

    // Show loading bar when navigating to a new page
    const links = document.querySelectorAll('a[href]');
    links.forEach(link => {
        link.addEventListener('click', function() {
            loadingBar.classList.remove('complete');
            loadingBar.classList.add('loading');
        });
    });
});