document.addEventListener("DOMContentLoaded", function() {
    const taskSearchInput = document.getElementById("taskSearch");

    taskSearchInput.addEventListener("input", function() {
        const query = taskSearchInput.value;

        // Send the AJAX request to the server
        fetch(`/filter_tasks`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ search_query: query }),
        })
        .then(response => response.json())
        .then(data => {
            console.log("Received data:", data);  // Debugging to see the received JSON
            const taskTableBody = document.getElementById("taskTableBody");
            taskTableBody.innerHTML = ""; // Clear the table body

            if (data.tasks && data.tasks.length > 0) {
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
            } else {
                taskTableBody.innerHTML = "<tr><td colspan='11'>No tasks found</td></tr>";
            }
        })
        .catch(error => console.error("Error fetching tasks:", error));
    });
});
