document.addEventListener('DOMContentLoaded', function() {
    const columns = document.querySelectorAll('.kanban-column');

    columns.forEach(column => {
        column.addEventListener('dragover', function(e) {
            e.preventDefault();
        });

        column.addEventListener('drop', function(e) {
            const taskId = e.dataTransfer.getData('text/plain');
            const taskCard = document.getElementById(taskId);
            this.appendChild(taskCard);

            // Update task status via AJAX
            const status = this.id;
            fetch(`/update_task_status`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ task_id: taskId, status: status })
            }).then(response => {
                if (!response.ok) {
                    console.error('Failed to update task status');
                }
            });
        });
    });

    const taskCards = document.querySelectorAll('.kanban-card');
    taskCards.forEach(card => {
        card.setAttribute('draggable', true);
        card.addEventListener('dragstart', function(e) {
            e.dataTransfer.setData('text/plain', card.id);
        });
    });
});