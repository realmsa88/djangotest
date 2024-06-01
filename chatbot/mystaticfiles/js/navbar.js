document.addEventListener('DOMContentLoaded', function() {
    var navbar = document.getElementById('navbar'); // Assuming your navbar has an ID of 'navbar'

    navbar.addEventListener('click', function(event) {
        var target = event.target;
        if (target.tagName === 'A') {
            // Handle navbar link click
            var href = target.getAttribute('href');
            if (href === '/administrator/accounts/register') {
                // Load content for the register page
                loadContent(href);
            } else {
                // Remove 'active' class from all navbar links
                document.querySelectorAll('.navbar-link').forEach(function(navLink) {
                    navLink.classList.remove('active');
                });
                
                // Add 'active' class to the clicked navbar link
                target.classList.add('active');
                
                // Load content based on the URL
                loadContent(href);
            }
        }
    });

    // Handle the initial loading of content and highlighting of the active navbar link
    var currentUrl = window.location.pathname;
    updateActiveNavbarLink(currentUrl);
    loadContent(currentUrl);
});

function loadContent(url) {
    // Fetch the HTML content of the specified URL
    fetch(url)
    .then(response => response.text())
    .then(html => {
        // Replace the content of the content container with the loaded HTML
        document.getElementById('content-container').innerHTML = html;

        // Remove unnecessary scripts from the loaded content
        document.getElementById('content-container').querySelectorAll('script').forEach(script => {
            script.parentNode.removeChild(script);
        });

        console.log('Content loaded successfully for URL:', url); // Debugging statement
    })
    .catch(error => console.error('Error loading content:', error));
}

function updateActiveNavbarLink(url) {
    // Remove 'active' class from all navbar links
    document.querySelectorAll('.navbar-link').forEach(function(navLink) {
        navLink.classList.remove('active');
    });

    // Add 'active' class to the navbar link corresponding to the current URL
    var activeNavLink = document.querySelector('.navbar-link[href="' + url + '"]');
    if (activeNavLink) {
        activeNavLink.classList.add('active');
    }
}
