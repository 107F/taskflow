document.addEventListener("DOMContentLoaded", function () {
    const fetchTaskBtn = document.getElementById("fetchTaskBtn");
    const taskIdInput = document.getElementById("task_id");

    // Elements for POS selection
    const posNameSelect = document.getElementById("pos_name");
    const posIDSelect = document.getElementById("pos_id");

    // Certified radio buttons
    const certifiedYesRadio = document.getElementById("certified_yes");
    const certifiedNoRadio = document.getElementById("certified_no");

    // Function to synchronize POS fields based on the selection
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

    // Fetch task data when the button is clicked
    fetchTaskBtn.addEventListener("click", function () {
        const taskId = taskIdInput.value;
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
            alert("Please enter a Task ID.");
        }
    });
});
