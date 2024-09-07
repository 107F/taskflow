document.addEventListener("DOMContentLoaded", function () {
    const taskIdInput = document.getElementById("task_id");
    const modifyBtn = document.getElementById("modifyBtn");

    // Elements for POS selection
    const posNameSelect = document.getElementById("pos_name");
    const posIDSelect = document.getElementById("pos_id");

    // Certified radio buttons
    const certifiedYesRadio = document.getElementById("certified_yes");
    const certifiedNoRadio = document.getElementById("certified_no");

    // Debugging: Check if elements are loaded
    console.log("DOM Loaded - Elements fetched: ", {
        taskIdInput,
        modifyBtn,
        posNameSelect,
        posIDSelect,
        certifiedYesRadio,
        certifiedNoRadio
    });

    // Function to synchronize POS fields based on selection
    function syncPosFields(event) {
        console.log("POS sync event triggered:", event.target.id);  // Debugging
        if (event.target === posNameSelect) {
            const selectedPosNameOption = posNameSelect.options[posNameSelect.selectedIndex];
            posIDSelect.value = selectedPosNameOption.getAttribute("data-pos-id");
            console.log("POS Name changed. Selected POS ID:", posIDSelect.value);  // Debugging
        } else if (event.target === posIDSelect) {
            const selectedPosIDOption = posIDSelect.options[posIDSelect.selectedIndex];
            posNameSelect.value = selectedPosIDOption.getAttribute("data-pos-name");
            console.log("POS ID changed. Selected POS Name:", posNameSelect.value);  // Debugging
        }
    }

    // Event listeners for POS selection
    posNameSelect.addEventListener("change", syncPosFields);
    posIDSelect.addEventListener("change", syncPosFields);

    // Function to clear all form fields
    function clearFormFields() {
        console.log("Clearing form fields.");  // Debugging
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
            console.log(`Fetching task data for Task ID: ${taskId}`);  // Debugging
            fetch(`/api/get_task/${taskId}`)
                .then(response => {
                    console.log("Server response:", response);  // Debugging
                    if (!response.ok) {
                        throw new Error("Network response was not ok");
                    }
                    return response.json();
                })
                .then(data => {
                    console.log("Data received:", data);  // Debugging
                    if (data.success) {
                        // Populate the form fields with the fetched task data
                        posNameSelect.value = data.task.pos_name;
                        posIDSelect.value = data.task.pos_id;
                        document.getElementById("description").value = data.task.task_desc;

                        // Ensure the status and priority radio buttons are properly selected
                        const statusRadio = document.querySelector(`input[name="status"][value="${data.task.task_status}"]`);
                        if (statusRadio) {
                            statusRadio.checked = true;
                            console.log(`Status set to: ${data.task.task_status}`);  // Debugging
                        }

                        const priorityRadio = document.querySelector(`input[name="priority"][value="${data.task.task_priority}"]`);
                        if (priorityRadio) {
                            priorityRadio.checked = true;
                            console.log(`Priority set to: ${data.task.task_priority}`);  // Debugging
                        }

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
                        console.log("Form populated with task data.");  // Debugging
                    } else {
                        alert(data.message || "Task not found!");
                        console.error("API Error:", data);  // Debugging
                    }
                })
                .catch(error => {
                    console.error('Error fetching task:', error);  // Debugging
                    alert('Error fetching task. Please check the console for more details.');
                });
        } else {
            console.log("No task ID provided. Clearing form.");  // Debugging
            // Clear all fields if taskId is empty
            clearFormFields();
        }
    }

    // Listen for changes in the task ID input field
    taskIdInput.addEventListener("input", function () {
        const taskId = taskIdInput.value.trim();
        console.log("Task ID input changed:", taskId);  // Debugging
        
        // Trigger fetch only if the input is not empty
        if (taskId) {
            fetchTaskData(taskId);
        } else {
            clearFormFields();
        }
    });

    // Function to modify task data
    function modifyTaskData() {
        const taskId = taskIdInput.value.trim();
        if (!taskId) {
            alert("Task ID is required to modify a task.");
            console.error("Task ID is missing.");  // Debugging
            return;
        }

        const formData = new FormData(document.getElementById("modifyTaskForm"));
        const formObject = {};
        formData.forEach((value, key) => formObject[key] = value);
        console.log("Form data being sent for modification:", formObject);  // Debugging

        fetch(`/modify`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formObject)
        })
        .then(response => {
            console.log("Response from server:", response);  // Debugging
            if (!response.ok) {
                throw new Error("Network response was not ok");
            }
            return response.json();
        })
        .then(data => {
            console.log("Data received from server:", data);  // Debugging
            if (data.success) {
                alert("Task modified successfully!");
                window.location.reload();  // Refresh the tasks table or fetch and re-render tasks dynamically
            } else {
                alert(data.message || "Failed to modify task.");
                console.error("Task modification failed:", data);  // Debugging
            }
        })
        .catch(error => {
            console.error('Error modifying task:', error);  // Debugging
            alert('Error modifying task. Please check the console for more details.');
        });
    }

    // Listen for clicks on the "Modify" button
    modifyBtn.addEventListener("click", function () {
        console.log("Modify button clicked.");  // Debugging
        modifyTaskData();
    });
});
