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
    const paginationContainer = document.getElementById("paginationContainer"); // Add a container for pagination controls

    let isPosIDUpdating = false;
    let isPosNameUpdating = false;
    let currentPage = 1; // Track the current page

    // Get today's date for setting placeholders
    function getTodayDate() {
        const today = new Date();
        const yyyy = today.getFullYear();
        const mm = String(today.getMonth() + 1).padStart(2, '0');
        const dd = String(today.getDate()).padStart(2, '0');
        return `${yyyy}-${mm}-${dd}`;
    }

    const todayDate = getTodayDate();
    setDateInputPlaceholders();

    function setDateInputPlaceholders() {
        startDateInput.value = todayDate;
        endDateInput.value = todayDate;
        startDateInput.placeholder = todayDate;
        endDateInput.placeholder = todayDate;
    }

    function getSelectedCheckboxValues(selector) {
        const checkboxes = document.querySelectorAll(selector);
        return Array.from(checkboxes)
            .filter(checkbox => checkbox.checked)
            .map(checkbox => checkbox.value);
    }

    // Fetch all POS Names and POS IDs for reset
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
    posIDSelect.addEventListener("change", function () {
        const selectedPosId = posIDSelect.value;
        if (selectedPosId) {
            fetchPosNames(selectedPosId);  // Fetch POS Names based on POS ID
        }
    });

    // Event listener for POS Name selection change
    posNameSelect.addEventListener("change", function () {
        const selectedPosName = posNameSelect.value;
        if (selectedPosName) {
            fetchPosNumbers(selectedPosName);  // Fetch POS Numbers based on POS Name
        }
    });

    // Fetch and display tasks based on filter and pagination
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
    filterBtn.addEventListener("click", function () {
        currentPage = 1; // Reset to the first page on new filter
        const data = collectFilterData();
        fetchAndDisplayTasks(data, currentPage);
    });

    // Collect filter data
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
    taskSearchInput.addEventListener("input", function () {
        currentPage = 1; // Reset to the first page on new search
        const data = collectFilterData();
        fetchAndDisplayTasks(data, currentPage);
    });

    // Event listener for the Clear Filter button
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
