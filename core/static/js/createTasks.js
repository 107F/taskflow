/*
 * Stefania Galatolo's JavaScript Magic
 * Developed in collaboration with ChatGPT 4o, because even the most brilliant minds need a little AI-powered magic wand now and then!
 * 
 * File: createTasks.js
 * 
 * Purpose: This file is responsible for handling the interactivity of the task creation form in the task management app. 
 * It manages the synchronization of Point of Sale (POS) fields (both POS Name and POS ID) to ensure consistency when the user selects a POS. 
 * Additionally, it enforces mutual exclusivity for the 'Certified True' and 'Certified False' checkboxes, 
 * ensuring that only one can be selected at a time.
 * 
 * Key Features:
 * - Synchronization between POS Name and POS ID dropdowns.
 * - Mutual exclusivity enforcement for 'Certified True' and 'Certified False' checkboxes.
 * - Event-driven architecture using JavaScript's event listeners to respond to user actions.
 * 
 * Correlation with Other Files:
 * - Works in conjunction with the HTML form elements that contain POS Name, POS ID, and certification checkboxes.
 * - Ensures data consistency before form submission, thereby aiding in maintaining data integrity within the backend database.
 * 
 * Flow:
 * 1. When the DOM content is fully loaded, the script initializes event listeners for the POS dropdowns and certification checkboxes.
 * 2. The `syncPosFields` function is triggered whenever a change event occurs on either POS dropdown, updating the corresponding field to keep them synchronized.
 * 3. The `handleCertifiedCheckboxes` function manages the certification checkboxes, ensuring only one checkbox can be selected at any given time.
 */

document.addEventListener("DOMContentLoaded", function () {
    // Elements for POS selection
    const posNameSelect = document.getElementById("pos_name"); // Dropdown for selecting POS Name
    const posIDSelect = document.getElementById("pos_id"); // Dropdown for selecting POS ID
    const certifiedTrueCheckbox = document.getElementById("certified_true"); // Checkbox for 'Certified True'
    const certifiedFalseCheckbox = document.getElementById("certified_false"); // Checkbox for 'Certified False'

    // Function to synchronize POS ID and POS Name based on selection
    // This function is called whenever the user changes the selected option in either the POS Name or POS ID dropdowns.
    // It updates the corresponding field to ensure consistency between the POS Name and POS ID.
    function syncPosFields(event) {
        if (event.target === posNameSelect) {
            // When POS Name is selected, update POS ID accordingly
            const selectedPosNameOption = posNameSelect.options[posNameSelect.selectedIndex];
            posIDSelect.value = selectedPosNameOption.getAttribute("data-pos-id");
        } else if (event.target === posIDSelect) {
            // When POS ID is selected, update POS Name accordingly
            const selectedPosIDOption = posIDSelect.options[posIDSelect.selectedIndex];
            posNameSelect.value = selectedPosIDOption.getAttribute("data-pos-name");
        }
    }

    // Event listeners for POS selection
    // These listeners call the `syncPosFields` function to keep the POS Name and POS ID fields synchronized.
    // This ensures that changing one field updates the other to maintain data integrity.
    posNameSelect.addEventListener("change", syncPosFields);
    posIDSelect.addEventListener("change", syncPosFields);

    // Function to ensure only one certified checkbox is selected at a time
    // This function is called when the user changes the state of either certification checkbox.
    // It enforces mutual exclusivity, ensuring that only one checkbox ('Certified True' or 'Certified False') can be selected at a time.
    function handleCertifiedCheckboxes(event) {
        if (event.target.checked) { // Only proceed if the checkbox is being checked
            if (event.target.id === "certified_true") {
                certifiedFalseCheckbox.checked = false; // Uncheck 'Certified False' if 'Certified True' is checked
            } else if (event.target.id === "certified_false") {
                certifiedTrueCheckbox.checked = false; // Uncheck 'Certified True' if 'Certified False' is checked
            }
        }
    }

    // Event listeners for Certified checkboxes
    // These listeners ensure mutual exclusivity between 'Certified True' and 'Certified False'.
    // They call the `handleCertifiedCheckboxes` function whenever the state of a checkbox is changed.
    certifiedTrueCheckbox.addEventListener("change", handleCertifiedCheckboxes);
    certifiedFalseCheckbox.addEventListener("change", handleCertifiedCheckboxes);
});
