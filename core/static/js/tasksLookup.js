/*
 * tasksLookup.js
 * 
 * This script handles:
 * - Fetching tasks from the server based on user input and filters.
 * - Filtering tasks by various criteria such as POS ID, POS Name, dates, status, and priority.
 * - Providing real-time search functionality as the user types.
 * - Implementing pagination to navigate through the tasks.
 * 
 * **Main Components:**
 * 1. Event Listeners: Attached to DOM elements like filter inputs, search box, and pagination controls.
 * 2. Fetch Operations: Sends requests to the server to retrieve data, populate dropdowns, and update the task table.
 * 3. Dynamic DOM Manipulation: Updates the task table and pagination controls based on server responses.
 * 
 * **Interactivity with Server and Other Files:**
 * - Communicates with the Flask backend (`/filter_tasks`, `/api/pos_names_and_ids`, etc.) to fetch and filter task data.
 * - Works alongside HTML templates and server-side routes defined in Flask to provide a dynamic task management experience.
 * - Directly manipulates HTML elements within `tasks.html` to display and filter tasks.
 */

document.addEventListener("DOMContentLoaded", function () {
    // Get references to DOM elements that are frequently used
    // These elements are used throughout the script to capture user inputs for filtering
    // and to display the fetched tasks.
    const taskSearchInput = document.getElementById("taskSearch");
    const filterBtn = document.getElementById("filterBtn");
    const clearFilterBtn = document.getElementById("clearFilterBtn");
    const taskTableBody = document.getElementById("taskTableBody");
    const posIDSelect = document.getElementById("filterPosID");
    const posNameSelect = document.getElementById("filterPosName");
    const startDateInput = document.getElementById("startDate");
    const endDateInput = document.getElementById("endDate");
    const paginationContainer = document.getElementById("paginationContainer"); // Container for pagination controls

    let isPosIDUpdating = false;  // Flags to prevent multiple simultaneous updates
    let isPosNameUpdating = false;
    let currentPage = 1; // Track the current page

    // Get today's date for setting placeholders
    // This function provides a formatted date string for today's date
    // used to set default values and placeholders for date inputs.
    function getTodayDate() {
        const today = new Date();
        const yyyy = today.getFullYear();
        const mm = String(today.getMonth() + 1).padStart(2, '0');
        const dd = String(today.getDate()).padStart(2, '0');
        return `${yyyy}-${mm}-${dd}`;
    }

    // Set date input placeholders to today's date
    const todayDate = getTodayDate();
    setDateInputPlaceholders();

    function setDateInputPlaceholders() {
        startDateInput.value = todayDate;
        endDateInput.value = todayDate;
        startDateInput.placeholder = todayDate;
        endDateInput.placeholder = todayDate;
    }

    // Helper function to get values of selected checkboxes
    // Collects all checked checkboxes matching the selector and returns their values.
    function getSelectedCheckboxValues(selector) {
        const checkboxes = document.querySelectorAll(selector);
        return Array.from(checkboxes)
            .filter(checkbox => checkbox.checked)
            .map(checkbox => checkbox.value);
    }

    // Fetch all POS Names and POS IDs for reset
    // This function fetches available POS names and IDs from the server
    // to populate the dropdowns with all available options.
    function fetchAllPosNamesAndIds() {
        fetch('/api/pos_names_and_ids')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Reset POS Name dropdown
                    posNameSelect.innerHTML = '<option value="">All</option>';
                    data.pos_names.forEach(posName => {
                        const option = document.createElement("option");
                        option.value = posName;
                        option.textContent = posName;
                        posNameSelect.appendChild(option);
                    });

                    // Reset POS ID dropdown
                    posIDSelect.innerHTML = '<option value="">All</option>';
                    data.pos_ids.forEach(posId => {
                        const option = document.createElement("option");
                        option.value = posId;
                        option.textContent = posId;
                        posIDSelect.appendChild(option);
                    });
                }
            })
            .catch(error => console.error("Error fetching POS Names and IDs:", error));
    }

    // Fetch POS Names based on selected POS ID
    // This function makes an API call to get POS names related to the selected POS ID
    // and updates the POS Name dropdown options.
    function fetchPosNames(posId) {
        if (!isPosIDUpdating) {
            isPosIDUpdating = true;
            fetch(`/api/pos_names?pos_id=${posId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        posNameSelect.innerHTML = '<option value="">All</option>'; // Reset options
                        data.pos_names.forEach(posName => {
                            const option = document.createElement("option");
                            option.value = posName;
                            option.textContent = posName;
                            posNameSelect.appendChild(option);
                        });
                        if (data.pos_names.length === 1) {
                            // If there's only one matching name, select it automatically
                            posNameSelect.value = data.pos_names[0];
                        }
                    }
                })
                .catch(error => console.error("Error fetching POS Names:", error))
                .finally(() => isPosIDUpdating = false);
        }
    }

    // Fetch POS IDs based on selected POS Name
    // This function makes an API call to get POS IDs related to the selected POS name
    // and updates the POS ID dropdown options.
    function fetchPosNumbers(posName) {
        if (!isPosNameUpdating) {
            isPosNameUpdating = true;
            fetch(`/api/pos_ids?pos_name=${posName}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        posIDSelect.innerHTML = '<option value="">All</option>'; // Reset options
                        data.pos_ids.forEach(posId => {
                            const option = document.createElement("option");
                            option.value = posId;
                            option.textContent = posId;
                            posIDSelect.appendChild(option);
                        });
                        if (data.pos_ids.length === 1) {
                            // If there's only one matching ID, select it automatically
                            posIDSelect.value = data.pos_ids[0];
                        }
                    }
                })
                .catch(error => console.error("Error fetching POS IDs:", error))
                .finally(() => isPosNameUpdating = false);
        }
    }

    // Event listener for POS ID selection change
    // Triggers fetching and updating of POS Names dropdown when POS ID changes.
    posIDSelect.addEventListener("change", function () {
        const selectedPosId = posIDSelect.value;
        if (selectedPosId) {
            fetchPosNames(selectedPosId);  // Fetch POS Names based on POS ID
        }
    });

    // Event listener for POS Name selection change
    // Triggers fetching and updating of POS IDs dropdown when POS Name changes.
    posNameSelect.addEventListener("change", function () {
        const selectedPosName = posNameSelect.value;
        if (selectedPosName) {
            fetchPosNumbers(selectedPosName);  // Fetch POS Numbers based on POS Name
        }
    });

    // Fetch and display tasks based on filter and pagination
    // This function sends a POST request to the server with the current filters
    // and renders the tasks in the table based on the response.
    function fetchAndDisplayTasks(data, page = 1) {
        console.log("Sending data to server:", data);

        data.page = page; // Include the current page number

        fetch("/filter_tasks", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        })
        .then(response => response.json())
        .then(data => {
            console.log("Received data:", data);

            taskTableBody.innerHTML = ""; // Clear the table body

            if (data.tasks && data.tasks.length > 0) {
                // Iterate through the tasks and append them to the table
                data.tasks.forEach(task => {
                    const row = `
                    <tr>
                        <td>${task.task_id || 'n/a'}</td>
                        <td>${task.pos_id || 'n/a'}</td>
                        <td>${task.pos_name || 'n/a'}</td>
                        <td>${task.rec_date || 'n/a'}</td>
                        <td>${task.rec_certified || 'n/a'}</td>
                        <td>${task.task_desc || 'n/a'}</td>
                        <td>${task.task_status || 'n/a'}</td>
                        <td>${task.task_priority || 'n/a'}</td>
                        <td>${task.blocker_desc || 'n/a'}</td>
                        <td>${task.blocker_responsible || 'n/a'}</td>
                        <td>${task.task_start_date || 'n/a'}</td>
                        <td>${task.task_due_date || 'n/a'}</td>
                        <td>${task.task_notes || 'n/a'}</td>
                    </tr>`;
                    taskTableBody.innerHTML += row;
                });
                console.log("Tasks rendered successfully.");
                updatePaginationControls(data.page, data.total_pages); // Update pagination controls
            } else {
                taskTableBody.innerHTML = "<tr><td colspan='13'>No tasks found</td></tr>";
            }
        })
        .catch(error => console.error("Error fetching tasks:", error));
    }

    // Event listener for the Filter button
    // Triggers a fetch request to get tasks based on the current filter criteria.
    filterBtn.addEventListener("click", function () {
        currentPage = 1; // Reset to the first page on new filter
        const data = collectFilterData();
        fetchAndDisplayTasks(data, currentPage);
    });

    // Collect filter data from inputs
    // Collects data from all filter inputs to be sent to the server for task filtering.
    function collectFilterData() {
        const posID = posIDSelect.value;
        const posName = posNameSelect.value;
        const searchQuery = taskSearchInput.value;
        const startDate = startDateInput.value !== todayDate ? startDateInput.value : null;
        const endDate = endDateInput.value !== todayDate ? endDateInput.value : null;
        const selectedStatuses = getSelectedCheckboxValues("input[id^='status']");
        const selectedPriorities = getSelectedCheckboxValues("input[id^='priority']");

        return {
            pos_id: posID,
            pos_name: posName,
            search_query: searchQuery,
            start_date: startDate,
            end_date: endDate,
            statuses: selectedStatuses,
            priorities: selectedPriorities
        };
    }

    // Event listener for the search input field (dynamic filtering)
    // This provides real-time filtering as the user types in the search field.
    taskSearchInput.addEventListener("input", function () {
        currentPage = 1; // Reset to the first page on new search
        const data = collectFilterData();
        fetchAndDisplayTasks(data, currentPage);
    });

    // Event listener for the Clear Filter button
    // Clears all filters and resets the table to show all tasks.
    clearFilterBtn.addEventListener("click", function () {
        posIDSelect.value = "";
        posNameSelect.value = "";
        taskSearchInput.value = "";
        setDateInputPlaceholders();

        document.querySelectorAll("input[id^='status'], input[id^='priority']").forEach(checkbox => {
            checkbox.checked = false;
        });

        // Reset POS names and IDs
        fetchAllPosNamesAndIds();

        // Fetch tasks without any filters
        currentPage = 1; // Reset to the first page
        fetchAndDisplayTasks({}, currentPage);
    });

    // Initial fetch when the page loads
    fetchAndDisplayTasks({}, currentPage);

    // Update pagination controls
    // This function updates the pagination controls based on the current page and total pages.
    function updatePaginationControls(currentPage, totalPages) {
        paginationContainer.innerHTML = ""; // Clear existing controls

        // Previous link
        if (currentPage > 1) {
            const prevLink = document.createElement("a");
            prevLink.href = "#";
            prevLink.textContent = "Previous";
            prevLink.style.fontSize = "0.85em"; // Smaller font size
            prevLink.style.marginRight = "10px"; // Add some spacing
            prevLink.addEventListener("click", function (event) {
                event.preventDefault(); // Prevent default anchor behavior
                currentPage--;
                fetchAndDisplayTasks(collectFilterData(), currentPage);
            });
            paginationContainer.appendChild(prevLink);
        }

        // Page info
        const pageInfo = document.createElement("span");
        pageInfo.textContent = ` Page ${currentPage} of ${totalPages} `;
        pageInfo.style.fontSize = "0.85em"; // Smaller font size
        paginationContainer.appendChild(pageInfo);

        // Next link
        if (currentPage < totalPages) {
            const nextLink = document.createElement("a");
            nextLink.href = "#";
            nextLink.textContent = "Next";
            nextLink.style.fontSize = "0.85em"; // Smaller font size
            nextLink.style.marginLeft = "10px"; // Add some spacing
            nextLink.addEventListener("click", function (event) {
                event.preventDefault(); // Prevent default anchor behavior
                currentPage++;
                fetchAndDisplayTasks(collectFilterData(), currentPage);
            });
            paginationContainer.appendChild(nextLink);
        }
    }
});
