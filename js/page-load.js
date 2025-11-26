// Handle first-load animation
(function() {
    // Check if this is the first load
    const isFirstLoad = !sessionStorage.getItem('hasLoaded');
    
    if (isFirstLoad) {
        // Mark as first load
        document.body.classList.add('first-load');
        // Store that we've loaded the site
        sessionStorage.setItem('hasLoaded', 'true');
    }
})();
