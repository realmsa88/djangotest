  // Function to handle changing the number of entries per page
  function changeEntriesPerPage(select) {
    var selectedValue = select.value;
    if (selectedValue === 'all') {
        // Redirect to the same page without the "per_page" parameter
        var currentUrl = window.location.href;
        var newUrl = removeParamFromUrl(currentUrl, 'per_page');
        window.location.href = newUrl;
    } else {
        var currentUrl = window.location.href;
        var newUrl = addOrUpdateParamInUrl(currentUrl, 'per_page', selectedValue);
        window.location.href = newUrl;
    }
}

// Function to add or update a parameter in the URL
function addOrUpdateParamInUrl(url, param, value) {
    var newUrl = url;
    var regex = new RegExp('([?&])' + param + '=.*?(&|$)', 'i');
    if (newUrl.match(regex)) {
        newUrl = newUrl.replace(regex, '$1' + param + '=' + value + '$2');
    } else {
        var separator = newUrl.indexOf('?') !== -1 ? '&' : '?';
        newUrl = newUrl + separator + param + '=' + value;
    }
    return newUrl;
}

// Function to remove a parameter from the URL
function removeParamFromUrl(url, param) {
    var newUrl = url;
    var regex = new RegExp('([?&])' + param + '=.*?(&|$)', 'i');
    if (newUrl.match(regex)) {
        newUrl = newUrl.replace(regex, '$1');
        if (newUrl.endsWith('&') || newUrl.endsWith('?')) {
            newUrl = newUrl.slice(0, -1);
        }
    }
    return newUrl;
}

// Function to display all entries without pagination
function showAllEntries() {
    var rows = document.querySelectorAll('tbody tr');
    rows.forEach(function(row) {
        row.style.display = 'table-row';
    });
    // Hide pagination
    var pagination = document.querySelector('.pagination');
    if (pagination) {
        pagination.style.display = 'none';
    }
}

// Function to set the selected option in the dropdown menu based on the current URL query parameter
// Function to set the selected option in the dropdown menu based on the current URL query parameter
function setSelectedOption() {
    var currentUrl = window.location.href;
    var perPageParam = currentUrl.match(/(\?|&)per_page=\d+/);
    if (perPageParam) {
        var perPageValue = perPageParam[0].split('=')[1];
        document.getElementById('entries-per-page').value = perPageValue;
    } else {
        // If per_page parameter is not found, set the default value to "10"
        document.getElementById('entries-per-page').value = '5'; // Change '10' to whatever default value you want
    }
}

// Call the function to set the selected option when the page is loaded
setSelectedOption();


// Function to handle button clicks and filtering accounts
document.addEventListener('DOMContentLoaded', function() {
    // Get the filter buttons container
    var filterButtons = document.querySelector('.filter-buttons-container');

    // Function to handle button clicks
    filterButtons.addEventListener('click', function(event) {
        if (event.target.tagName === 'BUTTON') {
            var role = event.target.dataset.role; // Get the role from data-role attribute
            filterAccounts(role); // Call filter function
            highlightActiveButton(event.target); // Highlight the clicked button
        }
    });

    // Function to highlight the active button
    function highlightActiveButton(clickedButton) {
        // Remove 'current-active' class from all buttons
        document.querySelectorAll('.filter-buttons-container button').forEach(function(btn) {
            btn.classList.remove('current-active');
        });
        // Add 'current-active' class to the clicked button
        clickedButton.classList.add('current-active');
    }

    // Function to filter accounts based on the selected role
    function filterAccounts(role) {
        // Show only rows with the specified role
        var rows = document.querySelectorAll('tbody tr');
        rows.forEach(function(row) {
            var roleCell = row.querySelector('td:nth-last-child(2)').innerText.toLowerCase(); // Assuming role is in the second last column
            if (role === 'all' || roleCell.includes(role)) {
                row.style.display = 'table-row';
            } else {
                row.style.display = 'none';
            }
        });
    }

    // Initially highlight the 'All' button
    highlightActiveButton(document.getElementById('allBtn'));

    // Call the function to set the selected option when the page is loaded
    setSelectedOption();
});

// Function to handle showing details for a specific account
function showDetails(accountId) {
    // You can implement this function according to your needs
    console.log('Details for account with ID:', accountId);
}

// JavaScript code for showing account details in a modal
document.addEventListener('DOMContentLoaded', function() {
    // Get all details buttons
    var detailsButtons = document.querySelectorAll('.details-button');

    // Get the modal element
    var modal = document.getElementById('detailsModal');

    var accountidSpan = document.getElementById('accountID');
    var userEmailSpan = document.getElementById('userEmail');
    var fullNameSpan = document.getElementById('fullName');
    var userNameSpan = document.getElementById('userName');
    var phoneSpan = document.getElementById('phone');
    var addressSpan = document.getElementById('address');

    // Add click event listeners to details buttons
Array.from(detailsButtons).forEach(function(button) {
        button.addEventListener('click', function() {
            var accountID = button.dataset.account;
            var userEmail = button.dataset.email; // Get the user email from the button's dataset
            var fullName = button.dataset.name;
            var userName = button.dataset.us;
            var phone = button.dataset.phone;
            var address = button.dataset.address;

            console.log("User ID:", userID);
            
            accountidSpan.textContent = accountID;
            userEmailSpan.textContent = userEmail; // Set the user email in the modal content
            fullNameSpan.textContent = fullName;
            userNameSpan.textContent = userName;
            phoneSpan.textContent = phone;
            addressSpan.textContent = address;

            modal.style.display = "block"; // Show the modal
        });
    });

    // Get the <span> element that closes the modal
    var closeBtn = document.getElementsByClassName("close")[0];

    // When the user clicks on <span> (x), close the modal
    closeBtn.addEventListener('click', function() {
        modal.style.display = "none";
    });
});



function deleteAccount(button) {
var username = button.dataset.username; // Fetch username from the button dataset
fetch('/administrator/student/delete_account/' + username + '/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken()
    },
    body: JSON.stringify({ username: username })
})
.then(response => {
    if (!response.ok) {
        throw new Error('Network response was not ok');
    }
    return response.json();
})
.then(data => {
    if (data.success) {
        // Display a success message
        alert('User deleted successfully!');
        location.reload();
    } else {
        console.error('Failed to delete account:', data.error);
    }
})
.catch(error => {
    console.error('Error deleting account:', error);
    // Display an error message
    alert('Error deleting user: ' + error.message);
});
}



// Function to get the CSRF token
function getCSRFToken() {
var cookieValue = null;
if (document.cookie && document.cookie !== '') {
    var cookies = document.cookie.split(';');
    for (var i = 0; i < cookies.length; i++) {
        var cookie = cookies[i].trim();
        // Check if the cookie name matches the CSRF cookie name
        if (cookie.substring(0, 'csrftoken'.length + 1) === ('csrftoken' + '=')) {
            // Extract the CSRF token value
            cookieValue = decodeURIComponent(cookie.substring('csrftoken'.length + 1));
            break;
        }
    }
}
return cookieValue;
}

// Function to display the delete confirmation modal
function confirmDelete(button) {
var username = button.dataset.username;
var modal = document.getElementById('deleteConfirmationModal');
var deleteUsernameSpan = modal.querySelector('#deleteUsername');
deleteUsernameSpan.textContent = username;
modal.style.display = "block";
var closeBtn = modal.querySelector('.close');
closeBtn.addEventListener('click', function() {
    modal.style.display = "none";
});
window.addEventListener('click', function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
});
var confirmBtn = modal.querySelector('.confirm-delete');
confirmBtn.addEventListener('click', function() {
    deleteAccount(button); // Call the deleteAccount function
    modal.style.display = "none";
});
}

// JavaScript code to prevent closing the modal when clicking outside
document.addEventListener('DOMContentLoaded', function() {
// Get the delete confirmation modal
var deleteConfirmationModal = document.getElementById('deleteConfirmationModal');

// Add click event listener to the modal
deleteConfirmationModal.addEventListener('click', function(event) {
    // Check if the clicked element is the modal content
    if (event.target.closest('.modal-content')) {
        // If the clicked element is inside the modal content, do nothing
        return;
    } else {
        // If the clicked element is outside the modal content, prevent the default behavior
        event.stopPropagation();
    }
});
});




// Function to display the update confirmation modal
function confirmUpdate(button) {
var username = button.dataset.username;
var modal = document.getElementById('updateConfirmationModal');
var updateUsernameSpan = modal.querySelector('#updateUsername');
updateUsernameSpan.textContent = username;
modal.style.display = "block";
// Get the close button inside the update modal
var closeBtn = modal.querySelector('.close');

// Add click event listener to the close button
closeBtn.addEventListener('click', function() {
modal.style.display = "none"; // Close the update modal
});

window.addEventListener('click', function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
});
var confirmBtn = modal.querySelector('.confirm-update');
confirmBtn.addEventListener('click', function() {
    // Implement the update logic here
    modal.style.display = "none";
});
}

// Add click event listeners to all update icons
var updateIcons = document.querySelectorAll('.fa-pencil');
updateIcons.forEach(function(icon) {
icon.addEventListener('click', function() {
    var username = icon.parentElement.dataset.username;
    confirmUpdate(icon);
});
});

// Function to display the update modal
// Function to display the update modal
function showUpdateModal(username) {
var modal = document.getElementById('updateModal');
modal.style.display = "block";

// Get the close button inside the update modal
var closeBtn = modal.querySelector('.close');

// Add click event listener to the close button
closeBtn.addEventListener('click', function() {
modal.style.display = "none"; // Close the update modal
});

// Log any errors in the console
window.addEventListener('error', function(event) {
console.error('Error:', event.error);
});
}




var updateForm = document.getElementById('updateForm');
updateForm.addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent form submission
    
    // Get updated values from the form
    var updatedFirstName = document.getElementById('updateFirstName').value;
    var updatedLastName = document.getElementById('updateLastName').value;
    
    // Call function to update the account
    updateAccount(username, updatedFirstName, updatedLastName);
    
    modal.style.display = "none";
});


// Function to update the account
function updateAccount(username, updatedFirstName, updatedLastName) {
// Implement the logic to update the account details
console.log('Updating account with username:', username);
console.log('Updated First Name:', updatedFirstName);
console.log('Updated Last Name:', updatedLastName);
}

// Add click event listeners to all pencil icons
var pencilIcons = document.querySelectorAll('.fa-pencil');
pencilIcons.forEach(function(icon) {
icon.addEventListener('click', function() {
    var username = icon.parentElement.dataset.username;
    showUpdateModal(username);
});
});

// JavaScript code for showing account details in a modal
document.addEventListener('DOMContentLoaded', function() {
    // Get all details buttons and account cells
    var detailsButtons = document.querySelectorAll('.details-button');
    var accountCells = document.querySelectorAll('tbody tr td');

    // Get the modal element
    var modal = document.getElementById('detailsModal');

    var userEmailSpan = document.getElementById('userEmail');
    var fullNameSpan = document.getElementById('fullName');
    var userNameSpan = document.getElementById('userName');
    var phoneSpan = document.getElementById('phone');
    var addressSpan = document.getElementById('address');

    // Add click event listeners to details buttons and account cells
    detailsButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            showDetailsModal(button.dataset);
        });
    });

    accountCells.forEach(function(row) {
        row.addEventListener('click', function(event) {
            // Check if the click is not in the last column
            var isLastColumn = row.cellIndex === row.parentElement.cells.length - 1;
            if (!isLastColumn) {
                showDetailsModal(row.dataset);
            }
        });
    });

    // Function to show the details modal
    function showDetailsModal(data) {
        var userEmail = data.email; // Get the user email from the dataset
        var fullName = data.name;
        var userName = data.us;
        var phone = data.phone;
        var address = data.address;

        userEmailSpan.textContent = userEmail; // Set the user email in the modal content
        fullNameSpan.textContent = fullName;
        userNameSpan.textContent = userName;
        phoneSpan.textContent = phone;
        addressSpan.textContent = address;

        modal.style.display = "block"; // Show the modal
    }

    // Get the <span> element that closes the modal
    var closeBtn = document.getElementsByClassName("close")[0];

    // When the user clicks on <span> (x), close the modal
    closeBtn.addEventListener('click', function() {
        modal.style.display = "none";
    });
});

document.getElementById('search-input').addEventListener('input', function() {
    var searchValue = this.value.toLowerCase();
    var rows = document.querySelectorAll('tbody tr');
    rows.forEach(function(row) {
        var name = row.querySelector('td').innerText.toLowerCase();
        if (name.includes(searchValue)) {
            row.style.display = 'table-row';
        } else {
            row.style.display = 'none';
        }
    });
});

// Add event listener to each table row
document.querySelectorAll('tbody tr').forEach(row => {
    // Select the first column containing the user's name
    const nameColumn = row.querySelector('td:first-child');
    
    // Add click event listener to the name column
    nameColumn.addEventListener('click', function(event) {
        // Retrieve user ID from the clicked row's data-id attribute
        var userID = this.dataset.id;
        
        // Display user ID in the modal
        document.getElementById('accountID').textContent = userID;

        // Show the modal
        document.getElementById('detailsModal').style.display = 'block';
        
        // Prevent the event from propagating to parent elements
        event.stopPropagation();
    });
});


