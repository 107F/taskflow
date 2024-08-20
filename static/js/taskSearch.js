document.addEventListener("DOMContentLoaded", function() {
    const taskSearchInput = document.getElementById("taskSearch");

    taskSearchInput.addEventListener("input", function() {
        const query = taskSearchInput.value;

        fetch(`/search_tasks?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                const taskTableBody = document.getElementById("taskTableBody");
                taskTableBody.innerHTML = ""; // Clear the table body

                data.tasks.forEach(task => {
                    const row = document.createElement("tr");

                    row.innerHTML = `
                        <td>${task.task_id}</td>
                        <td>${task.pos_id}</td>
                        <td>${task.pos_name}</td>
                        <td>${task.reconciliation_date}</td>
                        <td>${task.certified}</td>
                        <td>${task.description}</td>
                        <td>${task.status}</td>
                        <td>${task.priority}</td>
                        <td>${task.start_date}</td>
                        <td>${task.due_date}</td>
                        <td>${task.notes}</td>
                    `;

                    taskTableBody.appendChild(row);
                });
            });
    });
});
