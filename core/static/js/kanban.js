document.addEventListener("DOMContentLoaded", function () {
    // Get references to DOM elements
    const taskSearchInput = document.getElementById("taskSearch");
    const filterBtn = document.getElementById("filterBtn");
    const clearFilterBtn = document.getElementById("clearFilterBtn");
    const posIDSelect = document.getElementById("filterPosID");
    const posNameSelect = document.getElementById("filterPosName");
    const startDateInput = document.getElementById("startDate");
    const endDateInput = document.getElementById("endDate");
    const dueTodayBtn = document.getElementById("dueTodayBtn"); // Reference to "Due Today" button

    const backlogColumn = document.getElementById("backlog");
    const todoColumn = document.getElementById("todo");
    const inProgressColumn = document.getElementById("inprogress");
    const doneColumn = document.getElementById("done");

    let isPosIDUpdating = false;
    let isPosNameUpdating = false;

    // Set up date inputs
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

    function fetchAllPosNamesAndIds() {
        fetch('/api/pos_names_and_ids')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    posNameSelect.innerHTML = '<option value="">All</option>';
                    data.pos_names.forEach(posName => {
                        const option = document.createElement("option");
                        option.value = posName;
                        option.textContent = posName;
                        posNameSelect.appendChild(option);
                    });

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

    function fetchPosNames(posId) {
        if (!isPosIDUpdating) {
            isPosIDUpdating = true;
            fetch(`/api/pos_names?pos_id=${posId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        posNameSelect.innerHTML = '<option value="">All</option>';
                        data.pos_names.forEach(posName => {
                            const option = document.createElement("option");
                            option.value = posName;
                            option.textContent = posName;
                            posNameSelect.appendChild(option);
                        });
                        if (data.pos_names.length === 1) {
                            posNameSelect.value = data.pos_names[0];
                        }
                    }
                })
                .catch(error => console.error("Error fetching POS Names:", error))
                .finally(() => isPosIDUpdating = false);
        }
    }

    function fetchPosNumbers(posName) {
        if (!isPosNameUpdating) {
            isPosNameUpdating = true;
            fetch(`/api/pos_ids?pos_name=${posName}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        posIDSelect.innerHTML = '<option value="">All</option>';
                        data.pos_ids.forEach(posId => {
                            const option = document.createElement("option");
                            option.value = posId;
                            option.textContent = posId;
                            posIDSelect.appendChild(option);
                        });
                        if (data.pos_ids.length === 1) {
                            posIDSelect.value = data.pos_ids[0];
                        }
                    }
                })
                .catch(error => console.error("Error fetching POS IDs:", error))
                .finally(() => isPosNameUpdating = false);
        }
    }

    posIDSelect.addEventListener("change", function () {
        const selectedPosId = posIDSelect.value;
        if (selectedPosId) {
            fetchPosNames(selectedPosId);
        }
    });

    posNameSelect.addEventListener("change", function () {
        const selectedPosName = posNameSelect.value;
        if (selectedPosName) {
            fetchPosNumbers(selectedPosName);
        }
    });

    // Function to fetch and display tasks in Kanban board
    function fetchAndDisplayKanbanTasks(data) {
        fetch("/api/kanban_tasks", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        })
        .then(response => response.json())
        .then(data => {
            // Clear only the task cards inside each column while preserving the label
            backlogColumn.querySelectorAll('.task-card').forEach(e => e.remove());
            todoColumn.querySelectorAll('.task-card').forEach(e => e.remove());
            inProgressColumn.querySelectorAll('.task-card').forEach(e => e.remove());
            doneColumn.querySelectorAll('.task-card').forEach(e => e.remove());

            // Render tasks in the appropriate columns
            if (data.tasks && data.tasks.length > 0) {
                data.tasks.forEach(task => {
                    const taskCard = document.createElement("div");
                    taskCard.className = "card task-card mb-3";
                    taskCard.setAttribute("data-task-id", task.task_id);
                    taskCard.setAttribute("data-task-status", task.task_status); // To track status for drag-and-drop
                    taskCard.innerHTML = `
                        <div class="card-body">
                            <h5 class="card-title">${task.task_desc || 'No Description'}</h5>
                            <p class="card-text"><strong>Status:</strong> ${task.task_status}</p>
                            <p class="card-text"><strong>Priority:</strong> ${task.task_priority}</p>
                            <p class="card-text"><strong>Due Date:</strong> ${task.task_due_date}</p>
                        </div>
                    `;

                    // Append the task card directly to the relevant column
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
            } else {
                // Handle case where no tasks are found
                backlogColumn.innerHTML += "<p>No Backlog tasks found.</p>";
                todoColumn.innerHTML += "<p>No To Do tasks found.</p>";
                inProgressColumn.innerHTML += "<p>No In Progress tasks found.</p>";
                doneColumn.innerHTML += "<p>No Done tasks found.</p>";
            }

            // Reinitialize sortable for drag-and-drop functionality after rendering tasks
            initializeSortable();
        })
        .catch(error => console.error("Error fetching Kanban tasks:", error));
    }

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

    // "Due Today" button event listener
    dueTodayBtn.addEventListener("click", function () {
        const todayDate = getTodayDate();

        // Create a data object to send to the backend
        const data = {
            start_date: todayDate,
            end_date: todayDate
        };

        // Call the function to fetch and display tasks filtered by today's date
        fetchAndDisplayKanbanTasks(data);
    });

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

    clearFilterBtn.addEventListener("click", function () {
        posIDSelect.value = "";
        posNameSelect.value = "";
        taskSearchInput.value = "";
        setDateInputPlaceholders();

        document.querySelectorAll("input[id^='status'], input[id^='priority']").forEach(checkbox => {
            checkbox.checked = false;
        });

        fetchAllPosNamesAndIds();

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

    // Function to handle updating task status in the frontend and backend
    function handleTaskStatusUpdate(taskElement) {
        const taskId = taskElement.getAttribute('data-task-id');
        const previousStatus = taskElement.getAttribute('data-task-status');

        // Identify the new status based on the column where the task is dropped
        let newStatus = '';
        const parentColumnId = taskElement.parentElement.id;

        if (parentColumnId === 'backlog') {
            newStatus = 'Backlog';
        } else if (parentColumnId === 'todo') {
            newStatus = 'To Do';
        } else if (parentColumnId === 'inprogress') {
            newStatus = 'In Progress';
        } else if (parentColumnId === 'done') {
            newStatus = 'Done';
        }

        if (newStatus && newStatus !== previousStatus) {
            // Update the status in the UI
            const statusElement = Array.from(taskElement.querySelectorAll('.card-text')).find(p => p.innerText.includes('Status'));
            statusElement.innerHTML = `<strong>Status:</strong> ${newStatus}`;
            taskElement.setAttribute('data-task-status', newStatus);

            // Send the updated status to the backend
            fetch(`/api/update_task_status/${taskId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ status: newStatus })
            })
            .then(response => response.json())
            .then(data => {
                if (!data.success) {
                    console.error(`Failed to update task ${taskId} in the database.`);
                    // Revert the UI if the update fails
                    statusElement.innerHTML = `<strong>Status:</strong> ${previousStatus}`;
                    taskElement.setAttribute('data-task-status', previousStatus);
                }
            })
            .catch(error => {
                console.error(`Error updating task ${taskId} status:`, error);
                // Revert the UI in case of an error
                statusElement.innerHTML = `<strong>Status:</strong> ${previousStatus}`;
                taskElement.setAttribute('data-task-status', previousStatus);
            });
        }
    }

    // Initialize sortable for drag-and-drop functionality
    function initializeSortable() {
        new Sortable(backlogColumn, {
            group: 'kanban',
            animation: 150,
            onEnd: function (evt) {
                handleTaskStatusUpdate(evt.item);  // Call status update handler on drop
            }
        });

        new Sortable(todoColumn, {
            group: 'kanban',
            animation: 150,
            onEnd: function (evt) {
                handleTaskStatusUpdate(evt.item);  // Call status update handler on drop
            }
        });

        new Sortable(inProgressColumn, {
            group: 'kanban',
            animation: 150,
            onEnd: function (evt) {
                handleTaskStatusUpdate(evt.item);  // Call status update handler on drop
            }
        });

        new Sortable(doneColumn, {
            group: 'kanban',
            animation: 150,
            onEnd: function (evt) {
                handleTaskStatusUpdate(evt.item);  // Call status update handler on drop
            }
        });
    }
});
