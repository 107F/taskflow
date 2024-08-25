document.addEventListener("DOMContentLoaded", function () {
    const taskSearchInput = document.getElementById("taskSearch");
    const filterBtn = document.getElementById("filterBtn");
    const clearFilterBtn = document.getElementById("clearFilterBtn");
    const posIDSelect = document.getElementById("filterPosID");
    const posNameSelect = document.getElementById("filterPosName");
    const startDateInput = document.getElementById("startDate");
    const endDateInput = document.getElementById("endDate");
    const taskTableBody = document.getElementById("taskTableBody");

    // Helper function to get today's date in YYYY-MM-DD format
    function getTodayDate() {
        const today = new Date();
        const yyyy = today.getFullYear();
        const mm = String(today.getMonth() + 1).padStart(2, '0'); // Months are zero-based
        const dd = String(today.getDate()).padStart(2, '0');
        return `${yyyy}-${mm}-${dd}`;
    }

    // Function to fetch and display tasks
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
                    console.log("No tasks found"); // Debugging: Log when no tasks are found
                    taskTableBody.innerHTML = "<tr><td colspan='11'>No tasks found</td></tr>";
                }
            })
            .catch(error => console.error("Error fetching tasks:", error));
    }

    // Event listener for the search input field
    taskSearchInput.addEventListener("input", function () {
        const query = taskSearchInput.value;
        console.log("Search input changed:", query); // Debugging: Log search input changes

        // Fetch tasks based on search input
        fetchAndDisplayTasks({ search_query: query });
    });

    // Event listener for the Filter button
    filterBtn.addEventListener("click", function () {
        const posID = posIDSelect.value;
        const posName = posNameSelect.value;
        const searchQuery = taskSearchInput.value;
        const startDate = startDateInput.value !== getTodayDate() ? startDateInput.value : null; // Consider only if changed
        const endDate = endDateInput.value !== getTodayDate() ? endDateInput.value : null; // Consider only if changed

        const data = {
            pos_id: posID,
            pos_name: posName,
            search_query: searchQuery,
            start_date: startDate,
            end_date: endDate
        };

        console.log("Filter button clicked with criteria - POS ID:", posID, "POS Name:", posName,
            "Search Query:", searchQuery, "Start Date:", startDate,
            "End Date:", endDate); // Debugging: Log all filter criteria

        // Fetch tasks based on filter input
        fetchAndDisplayTasks(data);
    });

    // Event listener for the Clear Filter button
    clearFilterBtn.addEventListener("click", function () {
        console.log("Clear filter button clicked"); // Debugging: Log when clear filter button is clicked

        // Clear filters
        posIDSelect.value = "";
        posNameSelect.value = "";
        taskSearchInput.value = "";
        startDateInput.value = getTodayDate(); // Reset to today's date as placeholder
        endDateInput.value = getTodayDate(); // Reset to today's date as placeholder

        console.log("Filters reset - POS ID:", posIDSelect.value,
            "POS Name:", posNameSelect.value,
            "Search Query:", taskSearchInput.value,
            "Start Date:", startDateInput.value,
            "End Date:", endDateInput.value); // Debugging: Log reset filter criteria

        // Fetch tasks without any filters
        fetchAndDisplayTasks({
            search_query: "",
            pos_id: "",
            pos_name: "",
            start_date: null,
            end_date: null
        });
    });

    // Initialize date fields to today's date on page load as placeholders
    startDateInput.value = getTodayDate();
    endDateInput.value = getTodayDate();

    console.log("Page loaded - Start Date set to:", startDateInput.value,
        "End Date set to:", endDateInput.value); // Debugging: Log initial date values
});
