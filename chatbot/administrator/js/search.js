document.getElementById('search-input').addEventListener('input', function() {
    var searchValue = this.value.trim().toLowerCase(); // Trim whitespace and convert to lowercase

    // If the search query is empty, show all rows and return
    if (!searchValue) {
        showAllRows();
        return;
    }

    // Fetch all accounts from the backend
    fetchAllAccounts().then(function(allAccounts) {
        // Filter accounts based on the search query
        var filteredAccounts = allAccounts.filter(function(account) {
            // Customize this logic based on your account structure
            return account.name.toLowerCase().includes(searchValue) ||
                   account.email.toLowerCase().includes(searchValue) ||
                   account.role.toLowerCase().includes(searchValue);
        });

        // Display filtered accounts in the table
        displayFilteredAccounts(filteredAccounts);
    }).catch(function(error) {
        console.error('Error fetching accounts:', error);
    });
});

// Function to fetch all accounts from the backend
function fetchAllAccounts() {
    return fetch('/api/accounts')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        });
}

// Function to display filtered accounts in the table
function displayFilteredAccounts(accounts) {
    var rows = document.querySelectorAll('tbody tr');
    rows.forEach(function(row) {
        var account = accounts.find(function(acc) {
            // Customize this logic based on your account structure
            return acc.id === parseInt(row.dataset.accountId);
        });
        if (account) {
            row.style.display = 'table-row';
        } else {
            row.style.display = 'none';
        }
    });
}
