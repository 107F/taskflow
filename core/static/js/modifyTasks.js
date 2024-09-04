document.addEventListener("DOMContentLoaded", function () {
    const fetchTaskBtn = document.getElementById("fetchTaskBtn");
    const taskIdInput = document.getElementById("task_id");

    fetchTaskBtn.addEventListener("click", function () {
        const taskId = taskIdInput.value;
        if (taskId) {
            fetch(`/api/get_task/${taskId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        document.getElementById("pos_name").value = data.task.pos_name;
                        document.getElementById("pos_id").value = data.task.pos_id;
                        document.getElementById("description").value = data.task.task_desc;
                        document.getElementById("status" + data.task.task_status).checked = true;
                        document.getElementById("priority" + data.task.task_priority).checked = true;
                        document.getElementById("start_date").value = data.task.task_start_date;
                        document.getElementById("due_date").value = data.task.task_due_date;
                        document.getElementById("reconciliation_date").value = data.task.rec_date;
                        document.getElementById("notes").value = data.task.task_notes;
                        document.getElementById("blocker_desc").value = data.task.blocker_desc;
                        document.getElementById("blocker_responsible").value = data.task.blocker_responsible;

                        if (data.task.rec_certified === 'Yes') {
                            document.getElementById("certified_yes").checked = true;
                        } else {
                            document.getElementById("certified_no").checked = true;
                        }
                    } else {
                        alert("Task not found!");
                    }
                })
                .catch(error => {
                    console.error('Error fetching task:', error);
                });
        } else {
            alert("Please enter a Task ID.");
        }
    });
});
