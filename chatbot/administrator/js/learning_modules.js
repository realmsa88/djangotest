

function filterInstruments(button, major) {
    // Close all student boxes and reset positions
    closeAllStudentBoxes();
    resetAllBoxPositions();

    // Remove active class from all buttons
    var buttons = document.querySelectorAll('.filter-buttons-container button');
    buttons.forEach(function(btn) {
        btn.classList.remove('actives');
    });

    // Add active class to the clicked button
    if (button) {
        button.classList.add('actives');
    }
    
    var items = document.querySelectorAll('.student-box');
    items.forEach(function(item) {
        var itemMajor = item.getAttribute('data-major');
        var itemMinor = item.getAttribute('data-minor');
        
        if (itemMajor === major || itemMinor === major) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
}

function closeAllStudentBoxes() {
    var detailsContainers = document.querySelectorAll('.student-details-container');
    detailsContainers.forEach(function(container) {
        container.style.display = 'none';
    });
}

function resetAllBoxPositions() {
    var studentBoxes = document.querySelectorAll('.student-box');
    studentBoxes.forEach(function(box) {
        box.style.top = '0';
    });
}

var scrollbar = document.querySelector('.scrollbar');
var buttonWrapper = document.querySelector('.button-wrapper');

// Variables to keep track of initial mouse position and scroll position
var startX, startScrollLeft;

// Function to handle mouse down event on the scrollbar
scrollbar.addEventListener('mousedown', function(e) {
    startX = e.clientX;
    startScrollLeft = buttonWrapper.scrollLeft;

    // Add mousemove and mouseup event listeners to the document
    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', onMouseUp);
});

// Function to handle mouse move event on the document
function onMouseMove(e) {
    var deltaX = e.clientX - startX;
    buttonWrapper.scrollLeft = startScrollLeft - deltaX;
}

// Function to handle mouse up event on the document
function onMouseUp() {
    // Remove mousemove and mouseup event listeners from the document
    document.removeEventListener('mousemove', onMouseMove);
    document.removeEventListener('mouseup', onMouseUp);
}
var selectedBox = null; // Variable to store the currently selected box

var studentBoxes = document.querySelectorAll('.student-box');
studentBoxes.forEach(function(box) {
    box.addEventListener('click', function() {
        var detailsContainer = box.querySelector('.student-details-container');
        var isDetailsVisible = detailsContainer && window.getComputedStyle(detailsContainer).display === 'block';
        var chevronIcon = box.querySelector('i.fa-chevron-right');
        
        // Close all other student boxes and reset positions
        closeAllStudentBoxes();
        resetAllBoxPositions();

        if (detailsContainer) {
            if (isDetailsVisible) {
                // If the details container is visible, hide it and reset positions of subsequent boxes
                detailsContainer.style.display = 'none';
                resetBoxPositionsAfter(box, detailsContainer.offsetHeight);
            } else {
                // If the details container is hidden, show it and shift subsequent boxes down
                detailsContainer.style.display = 'block';
                shiftBoxesDown(box);
            }
        }

        // Remove the 'selected' class and chevron-down from the previously selected box (if any)
        if (selectedBox) {
            selectedBox.classList.remove('selected');
            var previousChevron = selectedBox.querySelector('i.fa-chevron-down');
            if (previousChevron) {
                previousChevron.classList.replace('fa-chevron-down', 'fa-chevron-right');
                previousChevron.style.color = 'rgba(23, 23, 117, 0.526)';
            }
        }

        // Add the 'selected' class to the clicked box
        box.classList.add('selected');

        // Change chevron icon to down and color it white
        if (chevronIcon) {
            chevronIcon.classList.replace('fa-chevron-right', 'fa-chevron-down');
            chevronIcon.style.color = 'white';
        }

        // Update the selectedBox variable
        selectedBox = box;
    });

    // Add event listeners to prevent click event from bubbling up to the parent box
    var bookContainers = box.querySelectorAll('.book-container');
    bookContainers.forEach(function(bookContainer) {
        bookContainer.addEventListener('click', function(event) {
            event.stopPropagation(); // Stop the event from bubbling up
        });
    });

    var detailsContainers = box.querySelectorAll('.student-details-container');
    detailsContainers.forEach(function(detailsContainer) {
        detailsContainer.addEventListener('click', function(event) {
            event.stopPropagation(); // Stop the event from bubbling up
        });
    });
});

function shiftBoxesDown(clickedBox) {
    var detailsContainer = clickedBox.querySelector('.student-details-container');
    var totalBookHeight = detailsContainer.offsetHeight;

    var nextBox = clickedBox.nextElementSibling;
    while (nextBox) {
        nextBox.style.top = parseInt(nextBox.style.top || 0) + totalBookHeight + 'px';
        nextBox = nextBox.nextElementSibling;
    }
}

function resetBoxPositionsAfter(clickedBox, totalBookHeight) {
    var nextBox = clickedBox.nextElementSibling;
    while (nextBox) {
        nextBox.style.top = parseInt(nextBox.style.top || 0) - totalBookHeight + 'px';
        nextBox = nextBox.nextElementSibling;
    }
}