

const GRADE_EXAMS_API = "/api/v1/grade_exams"
const MAX_FILE_SIZE = 1024 * 1024 * 10

const examPaperToggle = document.getElementById("exam-paper-toggle")
const answerKeyToggle = document.getElementById("answer-key-toggle")
const examPaperFileInput = document.getElementById("exam-paper-file")
const answerKeyFileInput = document.getElementById("answer-key-file")
const studentPapersFileInput = document.getElementById("student-papers-file")
const studentPapersSubmitButton = document.getElementById("student-papers-submit-button")
const examPaperTextArea = document.getElementById("exam-paper-text")
const studentsPaperTextArea = document.getElementById("student-paper-text")
const answerKeyTextArea = document.getElementById("answer-key-text")
const gradingInstructionsTextArea = document.getElementById("grading-instructions-text")
const studentPapersList = document.getElementById("student-papers-list")
const examPaperUploadZoneLabel = document.getElementById("exam-paper-upload-zone-label")
const examPaperUploadZoneHint = document.getElementById("exam-paper-upload-zone-hint")
const answerKeyUploadZoneLabel = document.getElementById("answer-key-upload-zone-label")
const answerKeyUploadZoneHint = document.getElementById("answer-key-upload-zone-hint")
const gradesPaperBtn = document.getElementById("grade-papers-button")
const examPaperCard = document.getElementById("exam-paper-card")
const studentPapersCard = document.getElementById("student-papers-card")
const studentPapersCardError = document.getElementById("student-papers-card-error")
const examPaperCardError = document.getElementById("exam-paper-card-error")
const resultsSection = document.getElementById("results-section")
const resultsContent = document.getElementById("results-content")
const resultsBanner = document.getElementById("results-banner")
const resultsBannerText = document.getElementById("results-banner-text")
const resultsIcon = document.getElementById("results-icon")
const resultsTotalPapers = document.getElementById("results-total-papers")
const resultsSuccessfullyChecked = document.getElementById("results-successfully-checked")
const resultsFailed = document.getElementById("results-failed")
const resultsTotalMarks = document.getElementById("results-total-marks")
const resultsAverageMarks = document.getElementById("results-average-marks")
const resultsMinimumMarks = document.getElementById("results-minimum-marks")
const resultsMaximumMarks = document.getElementById("results-maximum-marks")
const overallResultsTableBody = document.getElementById("overall-results-table-body")
const studentSelect = document.getElementById("student-select")
const studentDetailedReportTableBody = document.getElementById("student-detailed-report-table-body")
const gradingResultsTableMarks = document.getElementById("grading-results-table-marks")
const loadingSection = document.getElementById("loading-section")
const loadingText = document.getElementById("loading-text")
resultsBanner.hidden = true

const examPaper = {}
const answerKey = {}
const answerPapers = {}
const answerPaperSizes = {}
let count = 0;

// Display selected exam paper file name and size
examPaperFileInput.addEventListener("change", async function(event) {
    file = event.target.files[0];

    examPaper.name = file.name;
    examPaper.size = file.size;
    examPaper.data = await toPayLoad(file);

    examPaperUploadZoneLabel.textContent = file.name;
    examPaperUploadZoneHint.textContent = displayFileSize(file.size);
});


// Display selected answer key file name and size
answerKeyFileInput.addEventListener("change", async function(event) {
    file = event.target.files[0];

    answerKey.name = file.name;
    answerKey.size = file.size;
    answerKey.data = await toPayLoad(file);

    answerKeyUploadZoneLabel.textContent = file.name;
    answerKeyUploadZoneHint.textContent = displayFileSize(file.size);
});



// Add multiple answer paper files to list
studentPapersFileInput.addEventListener("change", async function(event) {
    const files = Array.from(event.target.files);

    for (const file of files) {
        count++;
        answerPapers[file.name] = await toPayLoad(file);
        answerPaperSizes[file.name] = file.size;

       displayStudentPapersList();
    }

    event.target.value = "";
});

// Add text answer paper to list
studentPapersSubmitButton.addEventListener("click", function() {
    const text = studentsPaperTextArea.value.trim();

    if (!text) return;

    let fileName;

    do {
        fileName = `Answer paper ${count + 1}`;
    } while (Object.hasOwn(answerPapers, fileName));

    answerPapers[fileName] = text;
    answerPaperSizes[fileName] = new Blob([text]).size;

    displayStudentPapersList();
    studentsPaperTextArea.value = "";
    count++;
});

// Display list of answer papers on screen
function displayStudentPapersList() {
    studentPapersList.replaceChildren();

    Object.entries(answerPapers).forEach(([fileName, fileData], i) => {
        const item = document.createElement("li");
        item.className = "paper-item";
        item.id = `student-paper-${i + 1}`;

        const thumb = document.createElement("span");
        thumb.className = "paper-item-thumb";
        thumb.innerHTML =
            '<svg class="icon"><use href="#icon-file"></use></svg>';

        const info = document.createElement("div");
        info.className = "paper-item-info";

        const name = document.createElement("p");
        name.className = "paper-item-name";
        name.textContent = fileName;

        const size = document.createElement("p");
        size.className = "paper-item-size";

        const bytes = answerPaperSizes[fileName] ?? 0;
        size.textContent = displayFileSize(bytes);

        info.append(name, size);

        const removeButton = document.createElement("button");
        removeButton.type = "button";
        removeButton.className = "paper-item-remove";
        removeButton.setAttribute("aria-label", `Remove ${fileName}`);
        removeButton.innerHTML =
            '<svg class="icon"><use href="#icon-close"></use></svg>';

        removeButton.addEventListener("click", function() {
            delete answerPapers[fileName];
            delete answerPaperSizes[fileName];
            displayStudentPapersList();
        });

        item.append(thumb, info, removeButton);
        studentPapersList.appendChild(item);
    });
}

function displayFileSize(bytes) {
    return bytes >= 1024 * 1024
        ? `${(bytes / (1024 * 1024)).toFixed(1)} MB`
        : `${(bytes / 1024).toFixed(1)} KB`;
}

gradesPaperBtn.addEventListener("click", async function() {
    if (validate()) {
    startGradingLoading();

        const examPaperText = examPaperToggle.checked ? examPaperTextArea.value : examPaper.data;
        let answerKeyText;
        if (!answerKeyToggle.checked) {
            if (answerKey.data) {
                answerKeyText = answerKey.data;
            } else {
                answerKeyText = "";
            }
        } else {
            answerKeyText = answerKeyTextArea.value;
        }
        grading = loadGradingScheme()
    
        try {
            response = await fetch(BASE_URL + GRADE_EXAMS_API, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    "exam_paper": examPaperText,
                    "answer_papers": answerPapers,
                    "answer_key": answerKeyText,
                    "instructions": gradingInstructionsTextArea.value,
                    "grading_scheme": loadGradingScheme(),
                }),
            }); 
            displayResultsContent(response, stopGradingLoading());
                
        } catch (error) {
            stopGradingLoading();

            resultsBannerText.textContent = "Your request could not be processed. Please try again";
            resultsBanner.classList.add("failure-banner")
            resultsIcon.classList.add("failure-banner-icon")
        }

        
    }
});

// Validate if exam paper & answer papers have been added
function validate() {
    let valid = true;

    if (examPaperToggle.checked) {
        if (!examPaperTextArea.value.trim()) {
            examPaperCard.classList.add("invalid-card");
            examPaperCardError.textContent = "Exam paper is required";
            invalid = false;
        } else {
            examPaperCard.classList.remove("invalid-card");
            examPaperCardError.textContent = " ";
        }
    } else {
        if (!examPaper.data) {
            examPaperCard.classList.add("invalid-card");
            examPaperCardError.textContent = "Exam paper is required";
            invalid = false;
        } else if (examPaper.size > MAX_FILE_SIZE) {
            examPaperCard.classList.add("invalid-card");
            examPaperCardError.textContent = "Exam paper size exceeds limit (10 MB)";
            invalid = false;
        } else {
            examPaperCard.classList.remove("invalid-card");
            examPaperCardError.textContent = " ";
        }
    }


    if (Object.keys(answerPapers).length === 0) {
        studentPapersCard.classList.add("invalid-card");
        studentPapersCardError.textContent = "At least one student paper is required";
        return false;
    }

   for (const [key, value] of Object.entries(answerPapers)) {
       if (answerPaperSizes[key]) {
           if (answerPaperSizes[key] > MAX_FILE_SIZE) {
               studentPapersCard.classList.add("invalid-card");
            studentPapersCardError.textContent = "Student paper size exceeds limit (10 MB)";
               return false;
           } 
       } 
    }

    studentPapersCard.classList.remove("invalid-card");
    studentPapersCardError.textContent = " ";
    return valid;
}

// Load grading scheme from session storage
function loadGradingScheme() {
    const gradingScheme = sessionStorage.getItem("gradingScheme");
    return gradingScheme ? JSON.parse(gradingScheme) : null;
}

// Display results
// Failure => Results banner
// Success => Results banner, stats, overall and detailed reports tables
let currentResults = null;   // latest response, used by the student dropdown

async function displayResultsContent(response, time) {
    const data = await response.json();

    // Reset from any previous run
    resultsBanner.classList.remove("success-banner", "failure-banner");
    resultsIcon.classList.remove("success-banner-icon", "failure-banner-icon");
    resultsContent.hidden = true;

    if (!response.ok || data["successful_papers"] == 0) {
        resultsBannerText.textContent = !response.ok
            ? "Your request could not be processed. Please try again"
            : "No papers could be checked.";
        resultsBanner.classList.add("failure-banner");
        resultsIcon.classList.add("failure-banner-icon");
        return;
    }

    currentResults = data;
    resultsBannerText.textContent = `Successfully checked ${data["successful_papers"]} of ${data["total_papers"]} papers in ` + time;
    resultsBanner.classList.add("success-banner");
    resultsIcon.classList.add("success-banner-icon");


    // Stats cards
    resultsTotalPapers.textContent = data["total_papers"];
    resultsSuccessfullyChecked.textContent = data["successful_papers"];
    resultsFailed.textContent = data["failed_papers"];
    resultsTotalMarks.textContent = data["total_marks"].toFixed(2);
    resultsAverageMarks.textContent = data["average_marks"].toFixed(2);
    resultsMinimumMarks.textContent = data["minimum_marks"].toFixed(2);
    resultsMaximumMarks.textContent = data["maximum_marks"].toFixed(2);

    // Overall results table + student dropdown
    overallResultsTableBody.replaceChildren();
    studentSelect.replaceChildren();

    let paperCount = 1;
    gradingResultsTableMarks.textContent = "Marks (" + data["total_marks"] + ")"
    for (let [paperKey, paper] of Object.entries(data["graded_answer_papers"])) {
        paper = asObject(paper)
        const row = document.createElement("tr")
        for (const value of [paperCount++, paper["roll_no"], paper["marks_obtained"], paper["grade"]]) {
            const cell = document.createElement("td");
            cell.textContent = value ?? "-";
            row.appendChild(cell);
        }
        overallResultsTableBody.appendChild(row);

        const option = document.createElement("option");
        option.value = paperKey;                       // the real key of the graded paper
        option.textContent = paper["roll_no"] ?? paperKey;
        studentSelect.appendChild(option);
    }

    resultsContent.hidden = false;
    showDetailedReport(studentSelect.value); 
    setSummaryDetails(asObject(data["exam_paper"]));
}

// One listener, added once (not inside displayResultsContent)
studentSelect.addEventListener("change", () => showDetailedReport(studentSelect.value));

function showDetailedReport(paperKey) {
    studentDetailedReportTableBody.replaceChildren();
    if (!currentResults) return;

    const gradedExam = asObject(currentResults["graded_answer_papers"][paperKey]);
    const formattedExam = asObject(currentResults["exam_paper"]);
    if (!gradedExam) return;

    if (gradedExam["objective"] != null) {
        gradedExam["objective"].forEach((gradedQuestion, i) => {
            appendSingleRowDetailedReport(formattedExam["objective"][i], gradedQuestion);
        });
    }
    if (gradedExam["subjective"] != null) {
        createNestedDetailedReport(formattedExam["subjective"], gradedExam["subjective"]);
    }
    setDetailedDetails(formattedExam, gradedExam);
}

// To create detailed result card of single student
function createNestedDetailedReport(examQuestions, gradedQuestions) {
    for (var i = 0; i < examQuestions.length; i++) {
        appendSingleRowDetailedReport(examQuestions[i], gradedQuestions[i]);
        if (examQuestions[i]["subquestions"] != null) {
            createNestedDetailedReport(examQuestions[i]["subquestions"], gradedQuestions[i]["subquestions"]);
        } 
    }  
}

// Reusable function to create single row in detailed report card
function appendSingleRowDetailedReport(examQuestion, gradedQuestion) {
    const row = document.createElement("tr"); 
    const questionId = document.createElement("td");
    questionId.textContent = examQuestion["question_id"]
    const total_marks = document.createElement("td")
    total_marks.textContent = examQuestion["marks"]
    const obtained_marks = document.createElement("td")
    obtained_marks.textContent = gradedQuestion["marks_obtained"]
    const reasoning = document.createElement("td")
    reasoning.textContent = gradedQuestion["reasoning"]
    row.append(questionId, total_marks, obtained_marks, reasoning);
    studentDetailedReportTableBody.appendChild(row); 
}

// To convert graded papers from string json to dict object
function asObject(value) {
    return typeof value === "string" ? JSON.parse(value) : value;
}

// For showing and cal time of response
let timerStart = 0;
let timerInterval = null;

function fomratDurationMMSS(ms) {
    const totalSeconds = Math.floor(ms / 1000);
    const minutes = String(Math.floor(totalSeconds / 60)).padStart(2, '0');
    const seconds = String(totalSeconds % 60).padStart(2, '0');
    return minutes + ":" + seconds;
}

function formatDurationMinsAndSecs(ms) {
  const totalSeconds = Math.floor(ms / 1000);
  const minutes = String(Math.floor(totalSeconds / 60)).padStart(2, '0');
  const seconds = String(totalSeconds % 60).padStart(2, '0');
  let output = ""
  if (minutes != 0) {
    output += minutes + " minutes and ";
  }
  return output + seconds + " seconds";
}

function startGradingLoading() {
  loadingSection.hidden = false;
  resultsBanner.hidden = true;
  gradesPaperBtn.disabled = true;
  resultsContent.hidden = true;
  timerStart = performance.now();
  timerInterval = setInterval(() => {
    loadingText.textContent = "Working for " + fomratDurationMMSS(performance.now() - timerStart);
  }, 100);
}

function stopGradingLoading() {
  loadingSection.hidden = true;
  resultsBanner.hidden = false;
  gradesPaperBtn.disabled = false;
  clearInterval(timerInterval);
  timerInterval = null;
  return formatDurationMinsAndSecs(performance.now() - timerStart);
}

// Convert file to bytes
async function tobytes(file) {
    // const bytes = new Uint8Array(await file.arrayBuffer());    
    return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.readAsDataURL(file);
            
            // FIX: Grab index [1] to isolate the clean Base64 string
            reader.onload = () => resolve(reader.result.split(',')[1]); 
            reader.onerror = error => reject(error);
    });
}

async function toPayLoad(file) {
    return {"data": await tobytes(file)};
}
 
// Downloading PDF & CSV of Summary and Indetailed tables
let summaryDetails = [];   
let detailedDetails = [];   

// First property that has a value
function pickField(obj, ...names) {
    for (const name of names) {
        if (obj && obj[name] !== undefined && obj[name] !== null && obj[name] !== "") return obj[name];
    }
    return undefined;
}

// Drops items whose value is null / undefined / empty
function cleanDetails(items) {
    return items.filter(([, value]) => value !== null && value !== undefined && value !== "");
}

// The API sometimes returns objects as JSON strings
function parseIfString(value) {
    return typeof value === "string" ? JSON.parse(value) : value;
}

// Call once after the grading response arrives (the whole parsed response)
function setSummaryDetails(examPaper) {
    console.log("Exam paper")
    console.log(typeof examPaper)
    summaryDetails = cleanDetails([
        ["Subject", pickField(examPaper, "subject")],     
        ["Subject ID", pickField(examPaper, "course_id")],           
        ["Date", pickField(examPaper, "date")],  
        ["Total Marks", examPaper["marks"]],
    ]);
}

// Call every time a student is selected in the detailed report
function setDetailedDetails(examPaper, gradedPaper) {
    const examMeta = parseIfString(examPaper) ?? {};
    detailedDetails = cleanDetails([
        ["Subject", pickField(examPaper, "subject")],
        ["Date", pickField(examPaper, "date")],
        ["Roll No", gradedPaper["roll_no"]],
        ["Name", pickField(gradedPaper, "name")],
        ["Total marks", examPaper["marks"]],
        ["Obtained marks", gradedPaper["marks_obtained"]],
        ["Grade", gradedPaper["grade"]]
    ]);
}

function getTableData(tableId) {
    const table = document.getElementById(tableId);
    const headers = [...table.querySelectorAll("thead th")].map(th => th.textContent.trim());
    const rows = [...table.querySelectorAll("tbody tr")].map(tr =>
        [...tr.querySelectorAll("td")].map(td => td.textContent.trim())
    );
    return { headers, rows };
}

function safeFileName(text) {
    return String(text).replace(/[^A-Za-z0-9_-]+/g, "_");
}

function saveBlob(blob, filename) {
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
}

// CSV
function csvCell(value) {
    let text = String(value ?? "");
    if (/^[=+@\t\r]/.test(text)) text = "'" + text;           // stops Excel running text as a formula
    return /[",\n\r]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
}

// Details first as "Label,Value" lines, then a blank line, then the table
function downloadCsv(headers, rows, filename, details = []) {
    const allRows = [...details, ...(details.length ? [[]] : []), headers, ...rows];
    const csv = "\uFEFF" + allRows.map(row => row.map(csvCell).join(",")).join("\r\n");   // BOM: Excel reads UTF-8
    saveBlob(new Blob([csv], { type: "text/csv;charset=utf-8" }), filename);
}

// PDF
function downloadPdf(title, headers, rows, filename, details = []) {
    if (!window.jspdf) {
        console.error("jsPDF is not loaded. Check the <script> tags in index.html.");
        return;
    }
    const doc = new window.jspdf.jsPDF();
    doc.setFontSize(14);
    doc.text(title, 14, 16);

    // Details in two columns under the title
    let y = 24;
    doc.setFontSize(10);
    details.forEach(([label, value], i) => {
        const x = i % 2 === 0 ? 14 : 110;
        doc.text(`${label}: ${value}`, x, y);
        if (i % 2 === 1 || i === details.length - 1) y += 6;
    });

    doc.autoTable({
        head: [headers],
        body: rows,
        startY: details.length ? y + 4 : 22,
        styles: { fontSize: 9, cellPadding: 3 },
        headStyles: { fillColor: [31, 28, 27] },               // same dark colour as the buttons
        alternateRowStyles: { fillColor: [246, 245, 243] },    // banded rows like the UI
    });
    doc.save(filename);
}

document.addEventListener("click", (event) => {
    const clicked = event.target.closest("button");
    if (!clicked) return;

    const select = document.getElementById("student-select");
    const roll = safeFileName(select?.selectedOptions[0]?.textContent.trim() || "student");

    const jobs = {
        "download-csv-button": () => {
            const { headers, rows } = getTableData("grading-results-table");
            if (rows.length) downloadCsv(headers, rows, "grading_results.csv", summaryDetails);
        },
        "download-pdf-button": () => {
            const { headers, rows } = getTableData("grading-results-table");
            if (rows.length) downloadPdf("Grading Results", headers, rows, "grading_results.pdf", summaryDetails);
        },
        "detail-result-download-csv-button": () => {
            const { headers, rows } = getTableData("student-detailed-report-table");
            if (rows.length) downloadCsv(headers, rows, `detailed_report_${roll}.csv`, detailedDetails);
        },
        "detail-result-download-pdf-button": () => {
            const { headers, rows } = getTableData("student-detailed-report-table");
            if (rows.length) downloadPdf(`Detailed Marks Report - ${roll}`, headers, rows, `detailed_report_${roll}.pdf`, detailedDetails);
        },
    };

    jobs[clicked.id]?.();
});

