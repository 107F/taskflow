document.addEventListener("DOMContentLoaded", function () {
    const taskIdInput = document.getElementById("task_id");
    const modifyBtn = document.getElementById("modifyBtn");

    // Elements for POS selection
    const posNameSelect = document.getElementById("pos_name");
    const posIDSelect = document.getElementById("pos_id");

    // Certified radio buttons
    const certifiedYesRadio = document.getElementById("certified_yes");
    const certifiedNoRadio = document.getElementById("certified_no");

    // Function to synchronize POS fields based on selection
    function syncPosFields(event) {
        if (event.target === posNameSelect) {
            const selectedPosNameOption = posNameSelect.options[posNameSelect.selectedIndex];
            posIDSelect.value = selectedPosNameOption.getAttribute("data-pos-id");
        } else if (event.target === posIDSelect) {
            const selectedPosIDOption = posIDSelect.options[posIDSelect.selectedIndex];
            posNameSelect.value = selectedPosIDOption.getAttribute("data-pos-name");
        }
    }

    // Event listeners for POS selection
    posNameSelect.addEventListener("change", syncPosFields);
    posIDSelect.addEventListener("change", syncPosFields);

    // Function to clear all form fields
    function clearFormFields() {
        posNameSelect.value = "";
        posIDSelect.value = "";
        document.getElementById("description").value = "";
        
        // Clear all status and priority radio buttons
        document.querySelectorAll('input[name="status"]').forEach(radio => radio.checked = false);
        document.querySelectorAll('input[name="priority"]').forEach(radio => radio.checked = false);

        document.getElementById("start_date").value = "";
        document.getElementById("due_date").value = "";
        document.getElementById("reconciliation_date").value = "";
        document.getElementById("notes").value = "";
        document.getElementById("blocker_desc").value = "";
        document.getElementById("blocker_responsible").value = "";

        // Clear certified radio buttons
        certifiedYesRadio.checked = false;
        certifiedNoRadio.checked = false;
    }

    // Function to fetch task data
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

                        // Set the certified radio buttons
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

    // Listen for changes in the task ID input field
    taskIdInput.addEventListener("input", function () {
        const taskId = taskIdInput.value.trim();
        
        // Trigger fetch only if the input is not empty
        fetchTaskData(taskId);
    });

    // Function to modify task data
    function modifyTaskData() {
        const taskId = taskIdInput.value.trim();
        if (!taskId) {
            alert("Task ID is required to modify a task.");
            return;
        }

        const formData = new FormData(document.getElementById("modifyTaskForm"));
        const formObject = {};
        formData.forEach((value, key) => formObject[key] = value);

        fetch(`/api/modify_task/${taskId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formObject)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error("Network response was not ok");
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                alert("Task modified successfully!");
                // Refresh the tasks table
                window.location.reload(); // or fetch and re-render tasks dynamically
            } else {
                alert(data.message || "Failed to modify task.");
            }
        })
        .catch(error => {
            console.error('Error modifying task:', error);
            alert('Error modifying task. Please check the console for more details.');
        });
    }

    // Listen for clicks on the "Modify" button
    modifyBtn.addEventListener("click", function () {
        modifyTaskData();
    });
});
