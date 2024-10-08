/*
 * kanban.js
 *
 * This script is responsible for handling the entire functionality of the Kanban board in the task management tool.
 * It manages task filtering, fetching tasks from the server, updating task statuses through a drag-and-drop interface, and initializing the Kanban board columns.
 * The script utilizes the Fetch API for backend communication and Sortable.js for implementing drag-and-drop functionality on the board.
 *
 * Key functionalities include:
 * - Fetching and displaying tasks in the Kanban board
 * - Filtering tasks based on search queries, POS IDs, POS Names, statuses, and priorities
 * - Updating task status through drag-and-drop interaction
 * - Ensuring synchronization of the front-end display with the backend database
 *
 * Inputs:
 * - User interactions such as searching, filtering, and dragging tasks
 * - API responses from the server containing task data, POS names, and POS IDs
 *
 * Outputs:
 * - Dynamically updated Kanban board reflecting the current state of tasks
 * - Visual feedback and task status updates sent to the backend
 */

// Runs when the DOM content is fully loaded
document.addEventListener("DOMContentLoaded", function () {
    // DOM elements references for task search, filtering, and Kanban columns
    // These elements are crucial for user interaction with the task filtering system and the Kanban board
    const taskSearchInput = document.getElementById("taskSearch"); // Input field for task search
    const filterBtn = document.getElementById("filterBtn"); // Button to apply filters
    const clearFilterBtn = document.getElementById("clearFilterBtn"); // Button to clear all filters
    const posIDSelect = document.getElementById("filterPosID"); // Dropdown for selecting POS IDs
    const posNameSelect = document.getElementById("filterPosName"); // Dropdown for selecting POS Names
    const startDateInput = document.getElementById("startDate"); // Input field for start date filter
    const endDateInput = document.getElementById("endDate"); // Input field for end date filter
    const dueTodayBtn = document.getElementById("dueTodayBtn"); // Button to filter tasks due today

    // DOM elements for Kanban columns, representing task statuses
    const backlogColumn = document.getElementById("backlog");
    const todoColumn = document.getElementById("todo");
    const inProgressColumn = document.getElementById("inprogress");
    const doneColumn = document.getElementById("done");

    // Flags to prevent multiple fetch calls during dropdown updates
    // These prevent duplicate network requests when updating dropdown options
    let isPosIDUpdating = false; 
    let isPosNameUpdating = false;

    /**
     * Sets up date inputs to show today's date by default
     * Used to provide a default filter for tasks due today, enhancing user experience
     */
    function getTodayDate() {
        const today = new Date();
        const yyyy = today.getFullYear();
        const mm = String(today.getMonth() + 1).padStart(2, '0');
        const dd = String(today.getDate()).padStart(2, '0');
        return `${yyyy}-${mm}-${dd}`;
    }

    // Today's date is computed once to be used as the default for date filters
    const todayDate = getTodayDate();
    setDateInputPlaceholders();

    /**
     * Sets placeholders and default values for date inputs to today's date
     * Ensures that the date inputs have user-friendly defaults
     */
    function setDateInputPlaceholders() {
        startDateInput.value = todayDate;
        endDateInput.value = todayDate;
        startDateInput.placeholder = todayDate;
        endDateInput.placeholder = todayDate;
    }

    /**
     * Gets the values of all selected checkboxes
     * @param {string} selector - CSS selector to identify the checkboxes
     * @returns {Array} - Array of values of checked checkboxes
     */
    function getSelectedCheckboxValues(selector) {
        const checkboxes = document.querySelectorAll(selector);
        return Array.from(checkboxes)
            .filter(checkbox => checkbox.checked)
            .map(checkbox => checkbox.value);
    }

    /**
     * Fetches all POS names and IDs to populate the dropdowns
     * Interacts with the backend API to get the list of POS names and IDs
     */
    function fetchAllPosNamesAndIds() {
        fetch('/api/pos_names_and_ids')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Populate POS Name dropdown with data received from the backend
                    posNameSelect.innerHTML = '<option value="">All</option>';
                    data.pos_names.forEach(posName => {
                        const option = document.createElement("option");
                        option.value = posName;
                        option.textContent = posName;
                        posNameSelect.appendChild(option);
                    });

                    // Populate POS ID dropdown with data received from the backend
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

    /**
     * Fetches POS Names based on selected POS ID
     * Prevents redundant fetches using a flag and updates the POS Name dropdown
     * @param {string} posId - The POS ID selected by the user
     */
    function fetchPosNames(posId) {
        if (!isPosIDUpdating) {
            isPosIDUpdating = true;
            fetch(`/api/pos_names?pos_id=${posId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Update POS Name dropdown based on POS ID selection
                        posNameSelect.innerHTML = '<option value="">All</option>';
                        data.pos_names.forEach(posName => {
                            const option = document.createElement("option");
                            option.value = posName;
                            option.textContent = posName;
                            posNameSelect.appendChild(option);
                        });
                        // Auto-select the only option if only one POS name is returned
                        if (data.pos_names.length === 1) {
                            posNameSelect.value = data.pos_names[0];
                        }
                    }
                })
                .catch(error => console.error("Error fetching POS Names:", error))
                .finally(() => isPosIDUpdating = false);
        }
    }

    /**
     * Fetches POS IDs based on selected POS Name
     * Prevents redundant fetches using a flag and updates the POS ID dropdown
     * @param {string} posName - The POS Name selected by the user
     */
    function fetchPosNumbers(posName) {
        if (!isPosNameUpdating) {
            isPosNameUpdating = true;
            fetch(`/api/pos_ids?pos_name=${posName}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Update POS ID dropdown based on POS Name selection
                        posIDSelect.innerHTML = '<option value="">All</option>';
                        data.pos_ids.forEach(posId => {
                            const option = document.createElement("option");
                            option.value = posId;
                            option.textContent = posId;
                            posIDSelect.appendChild(option);
                        });
                        // Auto-select the only option if only one POS ID is returned
                        if (data.pos_ids.length === 1) {
                            posIDSelect.value = data.pos_ids[0];
                        }
                    }
                })
                .catch(error => console.error("Error fetching POS IDs:", error))
                .finally(() => isPosNameUpdating = false);
        }
    }

    // Event listeners to update POS names/IDs when the dropdown selection changes
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

    /**
     * Fetches tasks based on the provided filter criteria and displays them on the Kanban board
     * This function clears existing tasks from the board and re-populates it with filtered tasks
     * @param {Object} data - The filter criteria to be sent to the backend
     */
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
            // Clear the task cards inside each column while preserving the label
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

    // Event listener for the filter button
    // Applies filters based on user input and fetches matching tasks
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
    // Fetches tasks due today and displays them on the Kanban board
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

    // Event listener for task search input
    // Fetches tasks based on the search query entered by the user
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

    // Event listener for the clear filter button
    // Clears all filter inputs and fetches all tasks without any filters
    clearFilterBtn.addEventListener("click", function () {
        // Clear filter inputs
        posIDSelect.value = "";
        posNameSelect.value = "";
        taskSearchInput.value = "";
        setDateInputPlaceholders();

        // Uncheck all checkboxes
        document.querySelectorAll("input[id^='status'], input[id^='priority']").forEach(checkbox => {
            checkbox.checked = false;
        });

        // Re-fetch POS names and IDs
        fetchAllPosNamesAndIds();

        // Fetch all tasks with no filters
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

    // Initial fetch of tasks when the page loads
    // This ensures the Kanban board is populated as soon as the user visits the page
    fetchAndDisplayKanbanTasks({});

    /**
     * Handles updating task status in both the frontend and backend
     * @param {HTMLElement} taskElement - The task element that has been dragged and dropped
     */
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

    /**
     * Initializes sortable for drag-and-drop functionality on each column
     * Uses Sortable.js to enable reordering of tasks within and across columns
     */
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
