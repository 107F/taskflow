document.addEventListener("DOMContentLoaded", function() {
    const filterBtn = document.getElementById("filterBtn");
    const clearFilterBtn = document.getElementById("clearFilterBtn");
    const posIDSelect = document.getElementById("filterPosID");
    const posNameSelect = document.getElementById("filterPosName");
    const searchInput = document.getElementById("taskSearch");
    const taskTableBody = document.getElementById("taskTableBody");

    // Event listener for the Filter button
    filterBtn.addEventListener("click", function() {
        const posID = posIDSelect.value;
        const posName = posNameSelect.value;
        const searchQuery = searchInput.value;

        const data = {
            pos_id: posID,
            pos_name: posName,
            search_query: searchQuery
        };

        fetch("/filter_tasks", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            taskTableBody.innerHTML = ""; // Clear existing tasks

            // Populate table with filtered tasks
            data.tasks.forEach(task => {
                const row = `<tr>
                    <td>${task.task_id}</td>
                    <td>${task.pos_id}</td>
                    <td>${task.pos_name}</td>
                    <td>${task.rec_date}</td>
                    <td>${task.rec_certified}</td>
                    <td>${task.task_desc}</td>
                    <td>${task.task_status}</td>
                    <td>${task.task_priority}</td>
                    <td>${task.task_start_date}</td>
                    <td>${task.task_due_date}</td>
                    <td>${task.task_notes}</td>
                </tr>`;
                taskTableBody.innerHTML += row;
            });
        })
        .catch(error => console.error("Error:", error));
    });

    // Event listener for the Clear Filter button
    clearFilterBtn.addEventListener("click", function() {
        posIDSelect.value = "";
        posNameSelect.value = "";
        searchInput.value = "";
        filterBtn.click(); // Trigger a refresh of the tasks table without any filters
    });
});
