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

    /**
     * getTodayDate
     * 
     * Returns today's date in 'YYYY-MM-DD' format.
     */
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

            // Check if any tasks were returned
            if (data.tasks && data.tasks.length > 0) {
                data.tasks.forEach(task => {
                    const taskCard = document.createElement("div");
                    taskCard.className = "card task-card mb-3";
                    taskCard.setAttribute("data-task-id", task.task_id);  // For tracking
                    taskCard.innerHTML = `
                        <div class="card-body">
                            <h5 class="card-title">${task.task_desc || 'No Description'}</h5>
                            <p class="card-text"><strong>Status:</strong> ${task.task_status}</p>
                            <p class="card-text"><strong>Priority:</strong> ${task.task_priority}</p>
                            <p class="card-text"><strong>Due Date:</strong> ${task.task_due_date}</p>
                        </div>
                    `;

                    // Place tasks into the correct column based on status
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
                console.log("Kanban tasks rendered as cards successfully.");
                initializeDragAndDrop();  // Initialize drag-and-drop after rendering tasks
            } else {
                backlogColumn.innerHTML = "<p>No Backlog tasks found.</p>";
                todoColumn.innerHTML = "<p>No To Do tasks found.</p>";
                inProgressColumn.innerHTML = "<p>No In Progress tasks found.</p>";
                doneColumn.innerHTML = "<p>No Done tasks found.</p>";
                console.log("No Kanban tasks found.");
            }
        })
        .catch(error => console.error("Error fetching Kanban tasks:", error));
    }

    // Initialize drag-and-drop functionality
    function initializeDragAndDrop() {
        const columns = [backlogColumn, todoColumn, inProgressColumn, doneColumn];

        columns.forEach(column => {
            new Sortable(column, {
                group: "kanban",
                animation: 150,
                onEnd: function (evt) {
                    const taskId = evt.item.getAttribute("data-task-id");
                    const newStatus = evt.to.id;  // The column id (backlog, todo, etc.) becomes the new status

                    // Translate the column id to a task status
                    let statusMap = {
                        backlog: "Backlog",
                        todo: "To Do",
                        inprogress: "In Progress",
                        done: "Done"
                    };

                    const updatedStatus = statusMap[newStatus];
                    console.log(`Task ${taskId} moved to ${updatedStatus}`);

                    // Update task status via API
                    updateTaskStatus(taskId, updatedStatus);
                }
            });
        });
    }

    // Update task status on the server when dragged to a new column
    function updateTaskStatus(taskId, newStatus) {
        fetch(`/api/update_task_status/${taskId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ status: newStatus })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log(`Task ${taskId} status updated successfully to ${newStatus}`);
            } else {
                console.error(`Error updating status for task ${taskId}`);
            }
        })
        .catch(error => console.error(`Error updating task status for task ${taskId}:`, error));
    }

    // Fetch POS Names based on selected POS ID
    function fetchPosNames(posId) {
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
                }
            })
            .catch(error => console.error("Error fetching POS Names:", error));
    }

    // Event listener for POS ID selection change
    posIDSelect.addEventListener("change", function () {
        const selectedPosId = posIDSelect.value;
        if (selectedPosId) {
            fetchPosNames(selectedPosId);  // Fetch POS Names based on POS ID
        } else {
            posNameSelect.innerHTML = '<option value="">All</option>'; // Reset POS Name if no POS ID is selected
        }
    });

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

        console.log("Filter button clicked with criteria:", data);
        fetchAndDisplayKanbanTasks(data);
    });

    // Event listener for the Clear Filter button
    clearFilterBtn.addEventListener("click", function () {
        posIDSelect.value = "";
        posNameSelect.value = "";
        setDateInputPlaceholders();
        taskSearchInput.value = "";

        document.querySelectorAll("input[id^='status'], input[id^='priority']").forEach(checkbox => {
            checkbox.checked = false;
        });

        fetchAndDisplayKanbanTasks({});
    });

    // Event listener for search input field
    taskSearchInput.addEventListener("input", function () {
        const query = taskSearchInput.value;
        console.log("Search input changed:", query); // Debugging: Log search input changes
        fetchAndDisplayKanbanTasks({ search_query: query });
    });

    // Initial fetch when the page loads
    fetchAndDisplayKanbanTasks({});
});
