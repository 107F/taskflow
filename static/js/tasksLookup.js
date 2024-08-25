/**
 * tasksLookup.js
 * 
 * This JavaScript file is responsible for handling the front-end functionality of the task filtering system
 * in the TaskFlow application. It provides the logic to fetch and display tasks based on various filters
 * including search queries, POS ID, POS Name, date ranges, status, and priority. The script also initializes
 * certain elements and handles user interactions like typing in the search bar, clicking filter buttons, and
 * clearing filters. The script makes AJAX requests to the server to fetch filtered data and updates the task
 * display table dynamically without requiring a full page reload.
 * 
 * Key Functions:
 * - Fetch and display tasks based on user input.
 * - Manage filter inputs and apply appropriate filters.
 * - Initialize date inputs and manage placeholder logic for date fields.
 * - Handle user interactions like filtering and clearing filters.
 */

document.addEventListener("DOMContentLoaded", function () {
    // Get references to DOM elements that are frequently used
    const taskSearchInput = document.getElementById("taskSearch");
    const filterBtn = document.getElementById("filterBtn");
    const clearFilterBtn = document.getElementById("clearFilterBtn");
    const taskTableBody = document.getElementById("taskTableBody");
    const posIDSelect = document.getElementById("filterPosID");
    const posNameSelect = document.getElementById("filterPosName");
    const startDateInput = document.getElementById("startDate");
    const endDateInput = document.getElementById("endDate");

    /**
     * getTodayDate
     * 
     * Returns today's date in 'YYYY-MM-DD' format. This function is used to set and check default date
     * values for date input fields.
     * 
     * @returns {string} Today's date formatted as 'YYYY-MM-DD'.
     */
    function getTodayDate() {
        const today = new Date();
        const yyyy = today.getFullYear();
        const mm = String(today.getMonth() + 1).padStart(2, '0'); // Months are zero-based in JavaScript
        const dd = String(today.getDate()).padStart(2, '0');
        return `${yyyy}-${mm}-${dd}`;
    }

    /**
     * getSelectedCheckboxValues
     * 
     * Collects the values of all checkboxes that are checked under the specified selector.
     * This is used to gather the selected statuses and priorities for filtering tasks.
     * 
     * @param {string} selector - CSS selector to identify the checkboxes to collect values from.
     * @returns {Array} Array of selected checkbox values.
     */
    function getSelectedCheckboxValues(selector) {
        const checkboxes = document.querySelectorAll(selector);
        return Array.from(checkboxes)
            .filter(checkbox => checkbox.checked)
            .map(checkbox => checkbox.value);
    }

    /**
     * fetchAndDisplayTasks
     * 
     * Sends an AJAX request to the server to fetch tasks based on the provided filter criteria.
     * The server response is used to dynamically update the task display table.
     * 
     * @param {Object} data - Filter criteria including search query, POS ID, POS Name, date range, statuses, and priorities.
     */
    function fetchAndDisplayTasks(data) {
        console.log("Sending data to server:", data); // Debugging: Log data sent to server

        fetch("/filter_tasks", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        })
        .then(response => response.json())
        .then(data => {
            console.log("Received data:", data); // Debugging: Log the received JSON
            taskTableBody.innerHTML = ""; // Clear the table body

            if (data.tasks && data.tasks.length > 0) {
                // If tasks are returned, render them in the table
                data.tasks.forEach(task => {
                    const row = `
                    <tr>
                        <td>${task.task_id}</td>
                        <td>${task.pos_id}</td>
                        <td>${task.pos_name}</td>
                        <td>${task.rec_date || task.reconciliation_date}</td>
                        <td>${task.rec_certified || task.certified}</td>
                        <td>${task.task_desc || task.description}</td>
                        <td>${task.task_status || task.status}</td>
                        <td>${task.task_priority || task.priority}</td>
                        <td>${task.task_start_date || task.start_date}</td>
                        <td>${task.task_due_date || task.due_date}</td>
                        <td>${task.task_notes || task.notes}</td>
                    </tr>`;
                    taskTableBody.innerHTML += row;
                });
                console.log("Tasks rendered successfully."); // Debugging: Log successful rendering
            } else {
                // If no tasks are returned, display a message indicating that
                console.log("No tasks found"); // Debugging: Log when no tasks are found
                taskTableBody.innerHTML = "<tr><td colspan='11'>No tasks found</td></tr>";
            }
        })
        .catch(error => console.error("Error fetching tasks:", error));
    }

    /**
     * Event listener for search input field
     * 
     * Fetches and displays tasks whenever the user types in the search bar.
     * The search query is used as a filter to dynamically update the task list.
     */
    taskSearchInput.addEventListener("input", function () {
        const query = taskSearchInput.value;
        console.log("Search input changed:", query); // Debugging: Log search input changes

        // Fetch tasks based on the search input
        fetchAndDisplayTasks({ search_query: query });
    });

    /**
     * Event listener for the Filter button
     * 
     * Gathers all filter criteria from the UI elements and triggers a fetch request to update the task list.
     * Treats today's date as a placeholder and only applies date filters if changed from the default value.
     */
    filterBtn.addEventListener("click", function () {
        const posID = posIDSelect.value;
        const posName = posNameSelect.value;
        const searchQuery = taskSearchInput.value;
        const startDate = startDateInput.value !== getTodayDate() ? startDateInput.value : null; // Only filter if date is changed
        const endDate = endDateInput.value !== getTodayDate() ? endDateInput.value : null; // Only filter if date is changed

        // Get selected statuses and priorities
        const selectedStatuses = getSelectedCheckboxValues("input[id^='status']");
        const selectedPriorities = getSelectedCheckboxValues("input[id^='priority']");

        // Prepare data object for filtering
        const data = {
            pos_id: posID,
            pos_name: posName,
            search_query: searchQuery,
            start_date: startDate,
            end_date: endDate,
            statuses: selectedStatuses,
            priorities: selectedPriorities
        };

        console.log("Filter button clicked with criteria - POS ID:", posID, "POS Name:", posName,
            "Search Query:", searchQuery, "Start Date:", startDate, "End Date:", endDate,
            "Selected Statuses:", selectedStatuses, "Selected Priorities:", selectedPriorities); // Debugging: Log filter criteria

        // Fetch tasks based on the collected filter criteria
        fetchAndDisplayTasks(data);
    });

    /**
     * Event listener for the Clear Filter button
     * 
     * Resets all filter inputs to their default values and fetches the full task list.
     * Ensures no filters are applied after clearing.
     */
    clearFilterBtn.addEventListener("click", function () {
        console.log("Clear filter button clicked"); // Debugging: Log when clear filter button is clicked

        // Reset all filter inputs to default values
        posIDSelect.value = "";
        posNameSelect.value = "";
        taskSearchInput.value = "";
        startDateInput.value = getTodayDate(); // Reset to today's date
        endDateInput.value = getTodayDate(); // Reset to today's date

        // Uncheck all status and priority checkboxes
        document.querySelectorAll("input[id^='status'], input[id^='priority']").forEach(checkbox => {
            checkbox.checked = false;
        });

        console.log("Filters reset to default values"); // Debugging: Log reset filter criteria

        // Fetch tasks without any filters
        fetchAndDisplayTasks({
            search_query: "",
            pos_id: "",
            pos_name: "",
            start_date: null, // No date filter
            end_date: null,   // No date filter
            statuses: [],
            priorities: []
        });
    });

    /**
     * Initialize date fields on page load
     * 
     * Sets the date input fields to today's date initially, treating them as placeholders.
     */
    startDateInput.value = getTodayDate();
    endDateInput.value = getTodayDate();

    console.log("Page loaded - Start Date set to:", startDateInput.value,
        "End Date set to:", endDateInput.value); // Debugging: Log initial date values
});
