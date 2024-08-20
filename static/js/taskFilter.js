document.addEventListener('DOMContentLoaded', function () {
    const filterButton = document.getElementById('filterBtn');
    const filterSection = document.getElementById('filterSection');
    const posIdDropdown = document.getElementById('filterPosID');
    const posNameDropdown = document.getElementById('filterPosName');
    const taskTableBody = document.getElementById('taskTableBody');
    const clearFilterButton = document.getElementById('clearFilterBtn');
    const taskSearch = document.getElementById('taskSearch');

    // Show/hide the filter section when the filter button is clicked
    filterButton.addEventListener('click', function () {
        if (filterSection.style.display === 'none' || !filterSection.style.display) {
            filterSection.style.display = 'block';
        } else {
            filterSection.style.display = 'none';
        }
    });

    // Function to fetch and display tasks based on selected filters
    function fetchTasks() {
        const posId = posIdDropdown.value;
        const posName = posNameDropdown.value;
        const searchQuery = taskSearch.value;

        fetch('/filter_tasks', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                pos_id: posId,
                pos_name: posName,
                search_query: searchQuery
            })
        })
        .then(response => response.json())
        .then(data => {
            // Clear the current table
            taskTableBody.innerHTML = '';

            // Populate the table with the filtered tasks
            data.tasks.forEach(task => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${task.task_id}</td>
                    <td>${task.pos_id}</td>
                    <td>${task.pos_name}</td>
                    <td>${task.reconciliation_date}</td>
                    <td>${task.certified}</td>
                    <td>${task.description}</td>
                    <td>${task.status}</td>
                    <td>${task.priority}</td>
                    <td>${task.start_date}</td>
                    <td>${task.due_date}</td>
                    <td>${task.notes}</td>
                `;
                taskTableBody.appendChild(row);
            });
        });
    }

    // Fetch tasks when the dropdown values change
    posIdDropdown.addEventListener('change', function() {
        posNameDropdown.selectedIndex = 0;  // Reset the POS Name dropdown
        fetchTasks();
    });

    posNameDropdown.addEventListener('change', function() {
        posIdDropdown.selectedIndex = 0;  // Reset the POS ID dropdown
        fetchTasks();
    });

    // Fetch tasks when the search field is used
    taskSearch.addEventListener('input', fetchTasks);

    // Clear filters and show all tasks when the "Clear Filter" button is clicked
    clearFilterButton.addEventListener('click', function () {
        posIdDropdown.selectedIndex = 0;
        posNameDropdown.selectedIndex = 0;
        taskSearch.value = '';
        fetchTasks();  // Fetch all tasks
    });
});
