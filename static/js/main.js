/**
 * PathFinder AI — Client-side Interaction and Charting Engine
 */

document.addEventListener("DOMContentLoaded", () => {
    initSidebarToggle();
    initRangeSliders();
    initPredictForm();
    initDeleteModal();
    initViewDetailsModal();
});

/* ==========================================================================
   Sidebar Responsive Toggle
   ========================================================================== */
function initSidebarToggle() {
    const toggleBtn = document.getElementById("mobileSidebarToggle");
    const sidebar = document.querySelector(".app-sidebar");
    
    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener("click", () => {
            sidebar.classList.toggle("show");
        });

        // Close sidebar when clicking outside on mobile
        document.addEventListener("click", (e) => {
            if (window.innerWidth < 992 && !sidebar.contains(e.target) && !toggleBtn.contains(e.target)) {
                sidebar.classList.remove("show");
            }
        });
    }
}

/* ==========================================================================
   Range Slider Synchronization
   ========================================================================== */
function initRangeSliders() {
    document.querySelectorAll(".form-range-sync").forEach(slider => {
        const targetId = slider.dataset.target;
        const targetElem = document.getElementById(targetId);
        if (targetElem) {
            slider.addEventListener("input", (e) => {
                targetElem.textContent = e.target.value;
            });
        }
    });
}

/* ==========================================================================
   Prediction Form Handling (AJAX & Validation)
   ========================================================================== */
let radarChartInstance = null;

function initPredictForm() {
    const form = document.getElementById("placementPredictForm");
    if (!form) return;

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const submitBtn = document.getElementById("predictSubmitBtn");
        const btnText = submitBtn.querySelector(".btn-text");
        const btnSpinner = submitBtn.querySelector(".spinner-border");
        const alertBox = document.getElementById("predictionAlert");
        const resultSection = document.getElementById("predictionResultSection");

        // Collect Programming Skills from checked badges
        const selectedSkills = [];
        document.querySelectorAll(".skill-tag-check:checked").forEach(cb => {
            selectedSkills.push(cb.value);
        });

        const payload = {
            student_name: document.getElementById("student_name").value.trim(),
            cgpa: parseFloat(document.getElementById("cgpa").value),
            aptitude_score: parseFloat(document.getElementById("aptitude_score").value),
            technical_score: parseFloat(document.getElementById("technical_score").value),
            communication_score: parseFloat(document.getElementById("communication_score").value),
            internships: parseInt(document.getElementById("internships").value, 10),
            projects: parseInt(document.getElementById("projects").value, 10),
            backlogs: parseInt(document.getElementById("backlogs").value, 10),
            programming_skills: selectedSkills.join(", "),
            preferred_domain: document.getElementById("preferred_domain").value
        };

        // Client-side quick check
        if (!payload.student_name) {
            showAlert("Please enter the student's full name.", "danger");
            return;
        }

        // Set Loading State
        submitBtn.disabled = true;
        btnText.textContent = "Analyzing Profile...";
        btnSpinner.classList.remove("d-none");
        hideAlert();

        try {
            const response = await fetch("/api/predict", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                showAlert(data.error || "An error occurred during prediction.", "danger");
                submitBtn.disabled = false;
                btnText.textContent = "Evaluate Placement Readiness";
                btnSpinner.classList.add("d-none");
                return;
            }

            // Render Output
            renderPredictionResults(data);
            resultSection.classList.remove("d-none");
            resultSection.scrollIntoView({ behavior: "smooth", block: "start" });

        } catch (err) {
            showAlert("Network communication error. Please try again.", "danger");
            console.error(err);
        } finally {
            submitBtn.disabled = false;
            btnText.textContent = "Evaluate Placement Readiness";
            btnSpinner.classList.add("d-none");
        }
    });
}

function renderPredictionResults(data) {
    // 1. Student Name & Meta
    document.getElementById("resStudentName").textContent = data.student_name;
    document.getElementById("resCategoryPill").textContent = data.predicted_category;
    document.getElementById("resCategoryPill").className = `category-pill ${data.category_badge}`;
    document.getElementById("resCategoryDesc").textContent = data.category_description;

    // 2. Probabilities & Readiness
    document.getElementById("resPlacementProb").textContent = `${data.placement_probability}%`;
    document.getElementById("resProbProgressBar").style.width = `${data.placement_probability}%`;
    document.getElementById("resReadinessScore").textContent = data.readiness_score;

    // SVG Circular Progress
    const circle = document.getElementById("readinessSvgCircle");
    if (circle) {
        const radius = circle.r.baseVal.value;
        const circumference = 2 * Math.PI * radius;
        const offset = circumference - (data.readiness_score / 100) * circumference;
        circle.style.strokeDasharray = `${circumference} ${circumference}`;
        circle.style.strokeDashoffset = offset;
        circle.style.stroke = data.category_color;
    }

    // 3. Pillar Assessments
    const a = data.assessments;
    document.getElementById("resAcadStatus").textContent = a.academic.status;
    document.getElementById("resAcadStatus").className = `badge ${a.academic.badge}`;
    document.getElementById("resAcadSummary").textContent = a.academic.summary;

    document.getElementById("resTechStatus").textContent = a.technical.status;
    document.getElementById("resTechStatus").className = `badge ${a.technical.badge}`;
    document.getElementById("resTechSummary").textContent = a.technical.summary;

    document.getElementById("resCommStatus").textContent = a.communication.status;
    document.getElementById("resCommStatus").className = `badge ${a.communication.badge}`;
    document.getElementById("resCommSummary").textContent = a.communication.summary;

    document.getElementById("resExpStatus").textContent = a.experience.status;
    document.getElementById("resExpStatus").className = `badge ${a.experience.badge}`;
    document.getElementById("resExpSummary").textContent = a.experience.summary;

    // 4. Recommendations List
    const recList = document.getElementById("resRecommendationsList");
    recList.innerHTML = "";
    a.recommendations.forEach(rec => {
        const li = document.createElement("li");
        li.className = "mb-2 d-flex align-items-start gap-2 text-muted";
        li.innerHTML = `<i class="bi bi-arrow-right-circle-fill text-primary mt-1"></i> <span>${rec}</span>`;
        recList.appendChild(li);
    });

    // 5. Domain Skill Gap Analysis
    const cg = data.career_guidance;
    document.getElementById("resDomainTitle").textContent = cg.title;
    
    const matchedContainer = document.getElementById("resMatchedSkills");
    matchedContainer.innerHTML = "";
    if (cg.matched_skills && cg.matched_skills.length > 0) {
        cg.matched_skills.forEach(s => {
            const badge = document.createElement("span");
            badge.className = "badge bg-success-subtle text-success border border-success-subtle me-1 mb-1";
            badge.textContent = `✓ ${s}`;
            matchedContainer.appendChild(badge);
        });
    } else {
        matchedContainer.innerHTML = "<small class='text-muted'>No matched skills detected.</small>";
    }

    const missingContainer = document.getElementById("resMissingSkills");
    missingContainer.innerHTML = "";
    if (cg.missing_skills && cg.missing_skills.length > 0) {
        cg.missing_skills.forEach(s => {
            const badge = document.createElement("span");
            badge.className = "badge bg-warning-subtle text-warning border border-warning-subtle me-1 mb-1";
            badge.textContent = `+ ${s}`;
            missingContainer.appendChild(badge);
        });
    }

    // 6. Radar Chart
    renderRadarChart(data.radar_data);
}

function renderRadarChart(radarData) {
    const ctx = document.getElementById("studentRadarChart");
    if (!ctx) return;

    if (radarChartInstance) {
        radarChartInstance.destroy();
    }

    radarChartInstance = new Chart(ctx, {
        type: "radar",
        data: {
            labels: radarData.labels,
            datasets: [{
                label: "Student Competency (Score / 100)",
                data: radarData.values,
                backgroundColor: "rgba(91, 75, 196, 0.2)",
                borderColor: "#5B4BC4",
                borderWidth: 2,
                pointBackgroundColor: "#5B4BC4",
                pointBorderColor: "#FFFFFF",
                pointRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    min: 0,
                    max: 100,
                    ticks: { stepSize: 20, display: false },
                    pointLabels: {
                        font: { size: 11, family: "'Plus Jakarta Sans', sans-serif", weight: "600" },
                        color: "#64748B"
                    },
                    grid: { color: "#E2E8F0" }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

function showAlert(message, type) {
    const alertBox = document.getElementById("predictionAlert");
    if (alertBox) {
        alertBox.className = `alert alert-${type} alert-dismissible fade show`;
        alertBox.innerHTML = `
            <i class="bi bi-exclamation-triangle-fill me-2"></i> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        alertBox.classList.remove("d-none");
    }
}

function hideAlert() {
    const alertBox = document.getElementById("predictionAlert");
    if (alertBox) {
        alertBox.classList.add("d-none");
    }
}

/* ==========================================================================
   Delete Record with Confirmation Modal
   ========================================================================== */
function initDeleteModal() {
    let targetRecordId = null;
    let targetRow = null;
    const deleteModalElem = document.getElementById("confirmDeleteModal");
    const confirmDeleteBtn = document.getElementById("confirmDeleteBtn");

    if (!deleteModalElem || !confirmDeleteBtn) return;

    const modalInstance = new bootstrap.Modal(deleteModalElem);

    document.querySelectorAll(".btn-delete-record").forEach(btn => {
        btn.addEventListener("click", (e) => {
            targetRecordId = btn.dataset.id;
            targetRow = btn.closest("tr");
            const studentName = btn.dataset.name || "this student";
            document.getElementById("deleteStudentName").textContent = studentName;
            modalInstance.show();
        });
    });

    confirmDeleteBtn.addEventListener("click", async () => {
        if (!targetRecordId) return;

        confirmDeleteBtn.disabled = true;
        try {
            const resp = await fetch(`/api/prediction/${targetRecordId}`, { method: "DELETE" });
            const data = await resp.json();

            if (resp.ok && data.success) {
                modalInstance.hide();
                if (targetRow) {
                    targetRow.style.transition = "opacity 0.4s";
                    targetRow.style.opacity = "0";
                    setTimeout(() => targetRow.remove(), 400);
                }
                showToast("Record deleted successfully.", "success");
            } else {
                showToast(data.error || "Failed to delete record.", "danger");
            }
        } catch (e) {
            showToast("Network error while deleting record.", "danger");
        } finally {
            confirmDeleteBtn.disabled = false;
        }
    });
}

/* ==========================================================================
   View Record Details Modal
   ========================================================================== */
let modalRadarChart = null;

function initViewDetailsModal() {
    const viewModalElem = document.getElementById("viewDetailsModal");
    if (!viewModalElem) return;

    const modalInstance = new bootstrap.Modal(viewModalElem);

    document.querySelectorAll(".btn-view-record").forEach(btn => {
        btn.addEventListener("click", async () => {
            const recordId = btn.dataset.id;
            try {
                const resp = await fetch(`/api/prediction/${recordId}`);
                const res = await resp.json();
                if (!resp.ok || !res.success) {
                    showToast("Could not fetch record details.", "danger");
                    return;
                }

                const d = res.data;
                document.getElementById("modalStudentName").textContent = d.student_name;
                document.getElementById("modalCategoryPill").textContent = d.predicted_category;
                document.getElementById("modalCategoryPill").className = `category-pill ${d.category_badge}`;
                document.getElementById("modalProbability").textContent = `${d.placement_probability}%`;
                document.getElementById("modalReadiness").textContent = d.readiness_score;
                document.getElementById("modalCGPA").textContent = d.cgpa;
                document.getElementById("modalAptitude").textContent = `${d.aptitude_score}/100`;
                document.getElementById("modalTech").textContent = `${d.technical_score}/10`;
                document.getElementById("modalComm").textContent = `${d.communication_score}/10`;
                document.getElementById("modalBacklogs").textContent = d.backlogs;
                document.getElementById("modalInternships").textContent = d.internships;
                document.getElementById("modalProjects").textContent = d.projects;
                document.getElementById("modalDomain").textContent = d.preferred_domain;

                // Render modal radar chart
                const ctx = document.getElementById("modalRadarChartCanvas");
                if (ctx) {
                    if (modalRadarChart) modalRadarChart.destroy();
                    modalRadarChart = new Chart(ctx, {
                        type: "radar",
                        data: {
                            labels: d.radar_data.labels,
                            datasets: [{
                                label: "Score",
                                data: d.radar_data.values,
                                backgroundColor: "rgba(91, 75, 196, 0.25)",
                                borderColor: "#5B4BC4",
                                borderWidth: 2,
                                pointBackgroundColor: "#5B4BC4"
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            scales: {
                                r: { min: 0, max: 100, ticks: { display: false } }
                            },
                            plugins: { legend: { display: false } }
                        }
                    });
                }

                modalInstance.show();

            } catch (err) {
                showToast("Error retrieving details.", "danger");
            }
        });
    });
}

function showToast(message, type = "info") {
    let container = document.getElementById("toastContainer");
    if (!container) {
        container = document.createElement("div");
        container.id = "toastContainer";
        container.className = "toast-container position-fixed bottom-0 end-0 p-3";
        container.style.zIndex = "1100";
        document.body.appendChild(container);
    }

    const toast = document.createElement("div");
    toast.className = `toast align-items-center text-bg-${type} border-0`;
    toast.setAttribute("role", "alert");
    toast.setAttribute("aria-live", "assertive");
    toast.setAttribute("aria-atomic", "true");
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;

    container.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast, { delay: 3500 });
    bsToast.show();
    toast.addEventListener("hidden.bs.toast", () => toast.remove());
}
