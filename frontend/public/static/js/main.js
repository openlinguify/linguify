/**
 * This script contains several functions and event listeners for handling user interactions on the website.
 * It includes search functionality, comment submission, module click handling, and course content toggling.
 */

// Import necessary scripts and libraries
<script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.11.8/dist/umd/popper.min.js" integrity="sha384-I7E8VVD/ismYTF4hNIPjVp/Zjvgyol6VFvRkX/vR+Vc4jQkC+hVqc2pM8ODewa9r" crossorigin="anonymous"></script>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-+0n0l4+Zb2UWpJ6j7U5p/RVv2v6p5Z6p7j5g8n7Zq5" crossorigin="anonymous"></script>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.min.js" integrity="sha384-0pUGZvbkm6XF6gxjEnlmuGrJXVbNuzT9qBBavbLwCsOGabYfZo0T0to5eqruptLy" crossorigin="anonymous"></script>


/**
 * Function to toggle the display of course content.
 * It changes the display style of the course content element between 'block' and 'none'.
 * @param {HTMLElement} element - The course card element that was clicked.
 */
function toggleCourseContent(element) {
    var content = element.querySelector('.course-content');
    if (content.style.display === 'none' || content.style.display === '') {
        content.style.display = 'block';
    } else {
        content.style.display = 'none';
    }
}