/**
 * modifyTasks.js
 * Developed by Stefania Galatolo, with a little help from ChatGPT 4.0.
 * (Coding is tough, and sometimes it's just better to have a co-pilot who never sleeps, right?)
 *
 * This script is responsible for handling the modification of tasks in the task management application.
 * It supports key operations such as:
 * - Synchronizing POS (Point of Sale) fields between their name and ID.
 * - Clearing the task modification form.
 * - Fetching existing task data from the server based on user input.
 * - Submitting modified task data back to the server for update.
 * 
 * This script interacts with the server using GET and POST requests and communicates with
 * specific API endpoints (`/api/get_task/{task_id}` and `/api/modify_task/{task_id}`).
 * 
 * Important connections:
 * - This file communicates with `app.py` in the backend, where Flask routes handle the task data requests.
 * - It also works with the HTML form elements on the `modify.html` template page, ensuring that task modification fields are synced.
 */

document.addEventListener("DOMContentLoaded", function () {
    // Get references to key elements within the document for task modification.
    const taskIdInput = document.getElementById("task_id"); // Input for the task ID, used to fetch and modify tasks.
    const modifyBtn = document.getElementById("modifyBtn"); // Button to trigger task modification.

    // Elements for POS (Point of Sale) selection
    const posNameSelect = document.getElementById("pos_name"); // Dropdown to select POS by name.
    const posIDSelect = document.getElementById("pos_id"); // Dropdown to select POS by ID.

    // Certified radio buttons for user to mark if the task is certified or not.
    const certifiedYesRadio = document.getElementById("certified_yes");
    const certifiedNoRadio = document.getElementById("certified_no");

    /**
     * Synchronizes POS fields between POS name and POS ID.
     * This ensures that when one field (POS name or POS ID) is updated, the corresponding
     * value in the other field is also updated to reflect the selected POS correctly.
     *
     * @param {Event} event - The change event triggered when the POS fields are modified.
     */
    function syncPosFields(event) {
        // If POS name is changed, update the POS ID field to match.
        if (event.target === posNameSelect) {
            const selectedPosNameOption = posNameSelect.options[posNameSelect.selectedIndex];
            posIDSelect.value = selectedPosNameOption.getAttribute("data-pos-id");
        } 
        // If POS ID is changed, update the POS name field to match.
        else if (event.target === posIDSelect) {
            const selectedPosIDOption = posIDSelect.options[posIDSelect.selectedIndex];
            posNameSelect.value = selectedPosIDOption.getAttribute("data-pos-name");
        }
    }

    // Attach event listeners to POS selection elements to ensure they stay synchronized.
    posNameSelect.addEventListener("change", syncPosFields);
    posIDSelect.addEventListener("change", syncPosFields);

    /**
     * Clears all form fields, resetting them to their default values.
     * This function is useful when no task is selected or when a task needs to be cleared
     * (e.g., when the user enters an invalid task ID).
     */
    function clearFormFields() {
        posNameSelect.value = ""; // Clear POS name
        posIDSelect.value = "";   // Clear POS ID
        document.getElementById("description").value = ""; // Clear description
        
        // Uncheck all status and priority radio buttons
        document.querySelectorAll('input[name="status"]').forEach(radio => radio.checked = false);
        document.querySelectorAll('input[name="priority"]').forEach(radio => radio.checked = false);

        document.getElementById("start_date").value = ""; // Clear start date
        document.getElementById("due_date").value = ""; // Clear due date
        document.getElementById("reconciliation_date").value = ""; // Clear reconciliation date
        document.getElementById("notes").value = ""; // Clear notes
        document.getElementById("blocker_desc").value = ""; // Clear blocker description
        document.getElementById("blocker_responsible").value = ""; // Clear blocker responsible person

        // Clear certified radio buttons
        certifiedYesRadio.checked = false;
        certifiedNoRadio.checked = false;
    }

    /**
     * Fetches task data from the server based on the provided task ID.
     * This function sends a GET request to the `/api/get_task/{task_id}` endpoint
     * to retrieve the task data. The form fields are then populated with the fetched task details.
     * 
     * @param {string} taskId - The ID of the task to fetch data for.
     * 
     * The server response should include task information such as POS, description, status, priority, 
     * and reconciliation details, which will be reflected in the form fields.
     */
    function fetchTaskData(taskId) {
        if (taskId) {
            fetch(`/api/get_task/${taskId}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error("Network response was not ok");
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        // Populate the form fields with the fetched task data
                        posNameSelect.value = data.task.pos_name;
                        posIDSelect.value = data.task.pos_id;
                        document.getElementById("description").value = data.task.task_desc;

                        // Ensure the status and priority radio buttons are properly selected
                        const statusRadio = document.querySelector(`input[name="status"][value="${data.task.task_status}"]`);
                        if (statusRadio) statusRadio.checked = true;

                        const priorityRadio = document.querySelector(`input[name="priority"][value="${data.task.task_priority}"]`);
                        if (priorityRadio) priorityRadio.checked = true;

                        document.getElementById("start_date").value = data.task.task_start_date;
                        document.getElementById("due_date").value = data.task.task_due_date;
                        document.getElementById("reconciliation_date").value = data.task.rec_date;
                        document.getElementById("notes").value = data.task.task_notes;
                        document.getElementById("blocker_desc").value = data.task.blocker_desc;
                        document.getElementById("blocker_responsible").value = data.task.blocker_responsible;

                        // Set the certified radio buttons based on the fetched data
                        if (data.task.rec_certified === 'Yes') {
                            certifiedYesRadio.checked = true;
                            certifiedNoRadio.checked = false;
                        } else if (data.task.rec_certified === 'No') {
                            certifiedYesRadio.checked = false;
                            certifiedNoRadio.checked = true;
                        } else {
                            certifiedYesRadio.checked = false;
                            certifiedNoRadio.checked = false;
                        }
                    } else {
                        alert(data.message || "Task not found!");
                        console.error("API Error:", data);
                    }
                })
                .catch(error => {
                    console.error('Error fetching task:', error);
                    alert('Error fetching task. Please check the console for more details.');
                });
        } else {
            // Clear all fields if taskId is empty
            clearFormFields();
        }
    }

    // Listen for changes in the task ID input field to trigger task data fetching.
    taskIdInput.addEventListener("input", function () {
        const taskId = taskIdInput.value.trim();
        
        // Trigger fetch only if the input is not empty
        if (taskId) {
            fetchTaskData(taskId);
        } else {
            clearFormFields();
        }
    });

    /**
     * Sends the modified task data to the server for updating the task.
     * This function gathers all the data from the form and sends a POST request
     * to the `/api/modify_task/{task_id}` endpoint to update the task details.
     */
    function modifyTaskData() {
        const taskId = taskIdInput.value.trim();
        if (!taskId) {
            alert("Task ID is required to modify a task.");
            return;
        }

        const formData = new FormData(document.getElementById("modifyTaskForm")); // Collect form data
        const formObject = {};
        formData.forEach((value, key) => formObject[key] = value); // Convert form data to object

        fetch(`/api/modify_task/${taskId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formObject) // Send form data as JSON
        })
        .then(response => {
            if (!response.ok) {
                console.error(`Server error: ${response.statusText}`);
                throw new Error("Error modifying task");
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                alert("Task modified successfully!");
                window.location.reload(); // Reload page upon success
            } else {
                alert(data.message || "Failed to modify task.");
            }
        })
        .catch(error => {
            console.error('Error modifying task:', error);
        });
    }

    // Listen for clicks on the "Modify" button to send the modified data.
    modifyBtn.addEventListener("click", function () {
        modifyTaskData();
    });
});
