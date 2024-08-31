document.addEventListener("DOMContentLoaded", function () {
    // Elements for POS selection
    const posNameSelect = document.getElementById("pos_name");
    const posIDSelect = document.getElementById("pos_id");
    const certifiedTrueCheckbox = document.getElementById("certified_true");
    const certifiedFalseCheckbox = document.getElementById("certified_false");

    // Function to synchronize POS ID and POS Name based on selection
    function syncPosFields(event) {
        if (event.target === posNameSelect) {
            // When POS Name is selected, update POS ID
            const selectedPosNameOption = posNameSelect.options[posNameSelect.selectedIndex];
            posIDSelect.value = selectedPosNameOption.getAttribute("data-pos-id");
        } else if (event.target === posIDSelect) {
            // When POS ID is selected, update POS Name
            const selectedPosIDOption = posIDSelect.options[posIDSelect.selectedIndex];
            posNameSelect.value = selectedPosIDOption.getAttribute("data-pos-name");
        }
    }

    // Event listeners for POS selection
    posNameSelect.addEventListener("change", syncPosFields);
    posIDSelect.addEventListener("change", syncPosFields);

    // Function to ensure only one certified checkbox is selected at a time
    function handleCertifiedCheckboxes(event) {
        if (event.target.checked) {
            if (event.target.id === "certified_true") {
                certifiedFalseCheckbox.checked = false;
            } else if (event.target.id === "certified_false") {
                certifiedTrueCheckbox.checked = false;
            }
        }
    }

    // Event listeners for Certified checkboxes
    certifiedTrueCheckbox.addEventListener("change", handleCertifiedCheckboxes);
    certifiedFalseCheckbox.addEventListener("change", handleCertifiedCheckboxes);
});