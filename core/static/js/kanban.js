document.addEventListener("DOMContentLoaded", function () {
    // Get references to DOM elements
    const taskSearchInput = document.getElementById("taskSearch");
    const filterBtn = document.getElementById("filterBtn");
    const clearFilterBtn = document.getElementById("clearFilterBtn");
    const posIDSelect = document.getElementById("filterPosID");
    const posNameSelect = document.getElementById("filterPosName");
    const startDateInput = document.getElementById("startDate");
    const endDateInput = document.getElementById("endDate");

    const backlogColumn = document.getElementById("backlog");
    const todoColumn = document.getElementById("todo");
    const inProgressColumn = document.getElementById("inprogress");
    const doneColumn = document.getElementById("done");

    // Variable to prevent infinite loops when auto-updating POS fields
    let isPosIDUpdating = false;
    let isPosNameUpdating = false;

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

    // Fetch and display tasks on the Kanban board
    function fetchAndDisplayKanbanTasks(data) {
        console.log("Sending data to server for Kanban:", data);

        fetch("/api/kanban_tasks", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        })
        .then(response => response.json())
        .then(data => {
            console.log("Received data for Kanban:", data);

            // Clear existing tasks
            backlogColumn.innerHTML = "";
            todoColumn.innerHTML = "";
            inProgressColumn.innerHTML = "";
            doneColumn.innerHTML = "";

            // Render tasks in the appropriate columns
            if (data.tasks && data.tasks.length > 0) {
                data.tasks.forEach(task => {
                    const taskCard = document.createElement("div");
                    taskCard.className = "card task-card mb-3";
                    taskCard.setAttribute("data-task-id", task.task_id);
                    taskCard.innerHTML = `
                        <div class="card-body">
                            <h5 class="card-title">${task.task_desc || 'No Description'}</h5>
                            <p class="card-text"><strong>Status:</strong> ${task.task_status}</p>
                            <p class="card-text"><strong>Priority:</strong> ${task.task_priority}</p>
                            <p class="card-text"><strong>Due Date:</strong> ${task.task_due_date}</p>
                        </div>
                    `;

                    if (task.task_status === "Backlog") {
                        backlogColumn.appendChild(taskCard);
                    } else if (task.task_status === "To Do") {
                        todoColumn.appendChild(taskCard);
                    } else if (task.task_status === "In Progress") {
                        inProgressColumn.appendChild(taskCard);
                    } else if (task.task_status === "Done") {
                        doneColumn.appendChild(taskCard);
                    }
                });
                console.log("Kanban tasks rendered successfully.");
            } else {
                backlogColumn.innerHTML = "<p>No Backlog tasks found.</p>";
                todoColumn.innerHTML = "<p>No To Do tasks found.</p>";
                inProgressColumn.innerHTML = "<p>No In Progress tasks found.</p>";
                doneColumn.innerHTML = "<p>No Done tasks found.</p>";
            }
        })
        .catch(error => console.error("Error fetching Kanban tasks:", error));
    }

    // Event listener for the Filter button
    filterBtn.addEventListener("click", function () {
        const posID = posIDSelect.value;
        const posName = posNameSelect.value;
        const startDate = startDateInput.value !== todayDate ? startDateInput.value : null;
        const endDate = endDateInput.value !== todayDate ? endDateInput.value : null;
        const selectedStatuses = getSelectedCheckboxValues("input[id^='status']");
        const selectedPriorities = getSelectedCheckboxValues("input[id^='priority']");
        const searchQuery = taskSearchInput.value;

        const data = {
            pos_id: posID,
            pos_name: posName,
            start_date: startDate,
            end_date: endDate,
            statuses: selectedStatuses,
            priorities: selectedPriorities,
            search_query: searchQuery
        };

        fetchAndDisplayKanbanTasks(data);
    });

    // Event listener for the search input field (dynamic filtering)
    taskSearchInput.addEventListener("input", function () {
        const query = taskSearchInput.value;
        const posID = posIDSelect.value;
        const posName = posNameSelect.value;
        const startDate = startDateInput.value !== todayDate ? startDateInput.value : null;
        const endDate = endDateInput.value !== todayDate ? endDateInput.value : null;
        const selectedStatuses = getSelectedCheckboxValues("input[id^='status']");
        const selectedPriorities = getSelectedCheckboxValues("input[id^='priority']");

        const data = {
            search_query: query,
            pos_id: posID,
            pos_name: posName,
            start_date: startDate,
            end_date: endDate,
            statuses: selectedStatuses,
            priorities: selectedPriorities
        };

        fetchAndDisplayKanbanTasks(data);
    });

    // Event listener for the Clear Filter button
    clearFilterBtn.addEventListener("click", function () {
        console.log("Clear filter button clicked");

        // Reset filters
        posIDSelect.value = "";
        posNameSelect.value = "";
        taskSearchInput.value = "";
        setDateInputPlaceholders();

        // Uncheck all status and priority checkboxes
        document.querySelectorAll("input[id^='status'], input[id^='priority']").forEach(checkbox => {
            checkbox.checked = false;
        });

        // Re-fetch all POS names and IDs after clearing the filters
        fetchAllPosNamesAndIds();

        // Fetch tasks without any filters
        fetchAndDisplayKanbanTasks({
            search_query: "",
            pos_id: "",
            pos_name: "",
            start_date: null,
            end_date: null,
            statuses: [],
            priorities: []
        });
    });

    // Initial fetch when the page loads
    fetchAndDisplayKanbanTasks({});
});
