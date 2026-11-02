const GET_GRADING_SCHEME_API = "/api/v1/get_grading_scheme";

const gradeBoundariesRows = document.getElementById("grade-boundaries-rows");
const addGradeBtn = document.getElementById("add-grade-button");
const resetSchemeBtn = document.getElementById("reset-scheme-button");
const saveSchemeBtn = document.getElementById("save-scheme-button");
const invalidGradingSchemeError = document.getElementById("invalid-grading-scheme-error");
const gradeBoundariesCard = document.getElementById("grade-boundaries-card");
const gradingSchemeSuccessBanner = document.getElementById("grading-scheme-success-banner");
const gradingSchemeSuccessBannerText = document.getElementById("grading-scheme-success-banner-text");

fetchGradingScheme();

// To not show success banner on first fetch
let firstFetch = true;

// Fetch the default grading scheme from backend at first run or whenever user resets
async function fetchGradingScheme() {
    try {
        const response = await fetch(`${BASE_URL}${GET_GRADING_SCHEME_API}`, {
            method: "GET",
            headers: { "Content-Type": "application/json" }
        });
        const gradingScheme = await response.json();
        displayGradingScheme(gradingScheme);
        clearSchemeError();
        saveGradingScheme(gradingScheme, "Reset to default grading scheme.");
    } catch (error) {
        invalidGradingSchemeError.innerText = "Could not load the grading scheme from the server.";
    }
}

function clearSchemeError() {
    invalidGradingSchemeError.innerText = " ";
    gradeBoundariesCard.classList.remove("invalid-card");
}

// Build ONE boundary row (used by both the fetched scheme and the Add grade button)
function createBoundaryRow(gradeName = "", max = "", min = "") {
    const boundary = document.createElement("div");
    boundary.classList.add("boundary-row");

    const grade = document.createElement("input");
    grade.classList.add("input-field");
    grade.type = "text";
    grade.value = gradeName;
    grade.setAttribute("aria-label", "Grade name");

    const maxPercentage = document.createElement("input");
    maxPercentage.classList.add("input-field");
    maxPercentage.type = "number";
    maxPercentage.min = 0;
    maxPercentage.max = 100;
    maxPercentage.value = max;
    maxPercentage.setAttribute("aria-label", "Maximum percentage");

    const minPercentage = document.createElement("input");
    minPercentage.classList.add("input-field");
    minPercentage.type = "number";
    minPercentage.min = 0;
    minPercentage.max = 100;
    minPercentage.value = min;
    minPercentage.setAttribute("aria-label", "Minimum percentage");

    const remove = document.createElement("button");
    remove.type = "button";
    remove.classList.add("paper-item-remove", "boundary-cell-center");
    remove.setAttribute("aria-label", gradeName ? `Remove grade ${gradeName}` : "Remove grade");
    remove.innerHTML = '<svg class="icon" viewBox="0 0 24 24"><path d="M6 6l12 12M18 6 6 18"/></svg>';

    boundary.append(grade, maxPercentage, minPercentage, remove);
    return boundary;
}

// Display grading scheme in boundaries table
function displayGradingScheme(gradingScheme) {
    gradeBoundariesRows.innerHTML = "";

    for (const [key, value] of Object.entries(gradingScheme)) {
        // Accepts { A: { max: 100, min: 90 } } or { A: [100, 90] }
        const max = Array.isArray(value) ? value[0] : value.max;
        const min = Array.isArray(value) ? value[1] : value.min;
        gradeBoundariesRows.appendChild(createBoundaryRow(key, max, min));
    }
}

// Add new empty boundary row
addGradeBtn.addEventListener("click", () => {
    gradeBoundariesRows.appendChild(createBoundaryRow());
});

// Remove button: ONE listener handles every row, including rows added later
gradeBoundariesRows.addEventListener("click", (event) => {
    const removeBtn = event.target.closest(".paper-item-remove");
    if (removeBtn) removeBtn.closest(".boundary-row").remove();
});

// Reset grading scheme to default
resetSchemeBtn.addEventListener("click", () => {
    fetchGradingScheme()
});

// Save updated grading scheme into session storage
saveSchemeBtn.addEventListener("click", () => {
    const gradingScheme = {};
    let hasDuplicateGrade = false;

    // Only rows inside the rows container (the header row also has class "boundary-row")
    for (const boundary of gradeBoundariesRows.querySelectorAll(".boundary-row")) {
        const grade = boundary.children[0].value.trim();
        const maxPercentage = boundary.children[1].value;
        const minPercentage = boundary.children[2].value;
        if (grade in gradingScheme) hasDuplicateGrade = true;
        gradingScheme[grade] = [maxPercentage, minPercentage];
    }
    if (!hasDuplicateGrade && validateGradingScheme(gradingScheme)) {
        saveGradingScheme(gradingScheme, "Your grading scheme is saved successfully.");
        clearSchemeError();
    } else {
        gradeBoundariesCard.classList.add("invalid-card");
        invalidGradingSchemeError.innerText = "Invalid grading scheme!";
        gradingSchemeSuccessBanner.hidden = true;
    }
});

// Validate: whole numbers, max >= min, within 0-100, no gaps, no overlaps, covers 0 to 100
function validateGradingScheme(gradingScheme) {
    const ranges = [];

    for (const [grade, [max, min]] of Object.entries(gradingScheme)) {
        if (grade === "" || max === "" || min === "") return false;

        const maxNum = Number(max);
        const minNum = Number(min);
        if (!Number.isInteger(maxNum) || !Number.isInteger(minNum)) return false;
        if (minNum < 0 || maxNum > 100 || minNum > maxNum) return false;

        ranges.push([minNum, maxNum]);
    }
    if (ranges.length === 0) return false;

    // Sorted by min, each range must start right after the previous one ends
    ranges.sort((a, b) => a[0] - b[0]);
    let expectedMin = 0;
    for (const [min, max] of ranges) {
        if (min !== expectedMin) return false; // gap or overlap
        expectedMin = max + 1;
    }
    return expectedMin === 101;
}

// Save grading scheme to session storage
function saveGradingScheme(gradingScheme, bannerText) {
    sessionStorage.setItem("gradingScheme", JSON.stringify(gradingScheme));
    
    if (firstFetch) {
       firstFetch = false;
    } else {
        gradingSchemeSuccessBannerText.textContent = bannerText;
        gradingSchemeSuccessBanner.hidden = false;
    }
}
