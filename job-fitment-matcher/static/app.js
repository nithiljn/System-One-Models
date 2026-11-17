/**
 * Frontend Controller for AI Job-Resume Fitment Matcher.
 * Handles user interactions, preset loading, API calls, and DOM rendering.
 * Styled in Deep Sea Blue & Aqua aesthetic with Skeleton Loader and zero emojis.
 */

document.addEventListener("DOMContentLoaded", () => {
    // DOM Element References
    const jobInput = document.getElementById("job-description-input");
    const resumeInput = document.getElementById("resume-content-input");
    const jobCharCount = document.getElementById("job-char-count");
    const resumeCharCount = document.getElementById("resume-char-count");

    // Action Buttons
    const evaluateBtn = document.getElementById("evaluate-btn");
    const evaluateBtnText = document.getElementById("evaluate-btn-text");
    const evaluateSpinner = document.getElementById("evaluate-spinner");
    const clearBtn = document.getElementById("clear-btn");

    // PDF Upload Controls & File Chip
    const uploadPdfBtn = document.getElementById("upload-pdf-btn");
    const resumeFileInput = document.getElementById("resume-file-input");
    const pdfChip = document.getElementById("pdf-chip");
    const pdfFilename = document.getElementById("pdf-filename");
    const removePdfBtn = document.getElementById("remove-pdf-btn");

    // Results Display Containers & Skeleton
    const skeletonLoader = document.getElementById("skeleton-loader");
    const resultsContainer = document.getElementById("results-container");
    const verdictBanner = document.getElementById("verdict-banner");
    const verdictTitle = document.getElementById("verdict-title");
    const verdictSubtitle = document.getElementById("verdict-subtitle");
    const fitTierBadge = document.getElementById("fit-tier-badge");
    const dealbreakerBadge = document.getElementById("dealbreaker-badge");
    const scoreText = document.getElementById("score-text");
    const scoreBar = document.getElementById("score-bar");
    const latencyMetric = document.getElementById("latency-metric");
    const tokenMetric = document.getElementById("token-metric");

    // Deep Audit Controls
    const auditBtn = document.getElementById("audit-btn");
    const auditSpinner = document.getElementById("audit-spinner");
    const auditContainer = document.getElementById("audit-container");
    const missingSkillsList = document.getElementById("missing-skills-list");
    const redFlagsList = document.getElementById("red-flags-list");
    const recommendationsList = document.getElementById("recommendations-list");

    // Error Alert Box
    const errorAlert = document.getElementById("error-alert");
    const errorMessage = document.getElementById("error-message");

    // Sample Datasets for Quick Testing
    const samplePresets = {
        jobDescription:
            "Senior Backend Engineer (Python). Requirements: 5+ years building production-grade REST microservices using Python and FastAPI. Deep hands-on experience with Docker containerization, Kubernetes cluster management, and PostgreSQL performance tuning. Strong familiarity with Redis caching and asynchronous job workers.",
        matchingResume:
            "Staff Software Engineer with 7 years of backend engineering experience. Architected high-throughput distributed microservices in Python and FastAPI supporting over 20,000 requests per second. Built containerized deployment pipelines using Docker and managed multi-tenant Kubernetes clusters. Optimized PostgreSQL queries and implemented Redis caching, cutting latency by 45%.",
        mismatchedResume:
            "Junior Graphic Designer with 1 year experience creating branding identity packages, social media banners, and typography layouts using Adobe Photoshop and Figma. Passionate about color theory, print layout, and UI wireframing. Possesses foundational awareness of HTML and CSS styling."
    };

    /**
     * Updates character counter indicators on textareas.
     */
    function updateCharacterCounts() {
        jobCharCount.textContent = `${jobInput.value.length} / 15,000 characters`;
        resumeCharCount.textContent = `${resumeInput.value.length} / 20,000 characters`;
    }

    jobInput.addEventListener("input", updateCharacterCounts);
    resumeInput.addEventListener("input", updateCharacterCounts);

    clearBtn.addEventListener("click", () => {
        jobInput.value = "";
        resumeInput.value = "";
        resumeFileInput.value = "";
        if (pdfFilename) pdfFilename.textContent = "";
        if (pdfChip) {
            pdfChip.classList.add("hidden");
            pdfChip.classList.remove("flex");
        }
        if (uploadPdfBtn) uploadPdfBtn.classList.remove("hidden");
        updateCharacterCounts();
        resultsContainer.classList.add("hidden");
        auditContainer.classList.add("hidden");
        skeletonLoader.classList.add("hidden");
        hideError();
    });

    /**
     * Remove Uploaded PDF Resume Handler
     * Clears candidate resume text, resets file input, and restores upload button.
     */
    if (removePdfBtn) {
        removePdfBtn.addEventListener("click", () => {
            resumeInput.value = "";
            resumeFileInput.value = "";
            if (pdfFilename) pdfFilename.textContent = "";
            if (pdfChip) {
                pdfChip.classList.add("hidden");
                pdfChip.classList.remove("flex");
            }
            if (uploadPdfBtn) uploadPdfBtn.classList.remove("hidden");
            updateCharacterCounts();
            hideError();
        });
    }

    /**
     * PDF Resume File Selection and Extraction Handler
     */
    if (uploadPdfBtn && resumeFileInput) {
        uploadPdfBtn.addEventListener("click", (e) => {
            if (uploadPdfBtn.tagName.toLowerCase() !== "label") {
                resumeFileInput.click();
            }
        });
    }

    if (resumeFileInput) {
        resumeFileInput.addEventListener("change", async (event) => {
            const file = event.target.files[0];
            if (!file) return;

            if (!file.name.toLowerCase().endsWith(".pdf")) {
                showError("Invalid file type. Please upload a PDF file (.pdf).");
                return;
            }

            if (file.size > 5 * 1024 * 1024) {
                showError("File size exceeds 5MB limit. Please upload a smaller PDF.");
                return;
            }

            hideError();
            if (uploadPdfBtn) {
                uploadPdfBtn.classList.add("pointer-events-none", "opacity-60");
                uploadPdfBtn.innerHTML = `
                    <div class="gold-spinner w-3 h-3"></div>
                    <span>Extracting...</span>
                `;
            }

            const formData = new FormData();
            formData.append("file", file);

            try {
                const response = await fetch("/api/extract-pdf", {
                    method: "POST",
                    body: formData,
                });

                if (!response.ok) {
                    const errData = await response.json();
                    throw new Error(errData.detail || "Failed to parse PDF file.");
                }

                const data = await response.json();
                resumeInput.value = data.text;
                updateCharacterCounts();

                // Display file chip with remove icon
                if (pdfFilename) pdfFilename.textContent = data.filename;
                if (uploadPdfBtn) uploadPdfBtn.classList.add("hidden");
                if (pdfChip) {
                    pdfChip.classList.remove("hidden");
                    pdfChip.classList.add("flex");
                }
            } catch (err) {
                if (pdfChip) {
                    pdfChip.classList.add("hidden");
                    pdfChip.classList.remove("flex");
                }
                if (uploadPdfBtn) uploadPdfBtn.classList.remove("hidden");
                showError(err.message);
            } finally {
                if (uploadPdfBtn) {
                    uploadPdfBtn.classList.remove("pointer-events-none", "opacity-60");
                    uploadPdfBtn.innerHTML = `
                        <svg class="w-3.5 h-3.5 text-[#c1a265]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path>
                        </svg>
                        <span>Upload PDF</span>
                    `;
                }
                resumeFileInput.value = "";
            }
        });
    }

    /**
     * Displays a clean error message banner.
     */
    function showError(text) {
        errorMessage.textContent = text;
        errorAlert.classList.remove("hidden");
    }

    /**
     * Hides the error banner.
     */
    function hideError() {
        errorAlert.classList.add("hidden");
    }

    const closeErrorBtn = document.getElementById("close-error-btn");
    if (closeErrorBtn) {
        closeErrorBtn.addEventListener("click", hideError);
    }

    /**
     * Triggers System-1 Fitment Evaluation via POST /api/evaluate-fitment.
     */
    evaluateBtn.addEventListener("click", async () => {
        hideError();

        const jobDescription = jobInput.value.trim();
        const resumeContent = resumeInput.value.trim();

        // Client-side length validation
        if (jobDescription.length < 30) {
            showError("Job Description must contain at least 30 non-empty characters.");
            return;
        }

        if (resumeContent.length < 30) {
            showError("Candidate Resume must contain at least 30 non-empty characters.");
            return;
        }

        // Show loading state with oceanic skeleton shimmer
        evaluateBtn.disabled = true;
        evaluateBtnText.textContent = "EVALUATING...";
        evaluateSpinner.classList.remove("hidden");
        resultsContainer.classList.add("hidden");
        auditContainer.classList.add("hidden");
        skeletonLoader.classList.remove("hidden");
        skeletonLoader.scrollIntoView({ behavior: "smooth" });

        const startTime = performance.now();

        try {
            const response = await fetch("/api/evaluate-fitment", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    job_description: jobDescription,
                    resume_content: resumeContent
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "Server error occurred during evaluation.");
            }

            const data = await response.json();
            const clientRoundtripMs = Math.round(performance.now() - startTime);

            // Hide skeleton and render live evaluation results
            skeletonLoader.classList.add("hidden");
            renderEvaluationResults(data, clientRoundtripMs);

        } catch (err) {
            skeletonLoader.classList.add("hidden");
            showError(err.message);
        } finally {
            evaluateBtn.disabled = false;
            evaluateBtnText.textContent = "EVALUATE FITMENT";
            evaluateSpinner.classList.add("hidden");
        }
    });

    /**
     * Renders System-1 evaluation metrics adhering to Midnight Blue & Gold theme.
     */
    function renderEvaluationResults(data, clientLatencyMs) {
        // 1. Verdict Banner Styling
        if (data.is_eligible && data.fit_tier === "Strong Match") {
            verdictBanner.className = "p-6 rounded-lg border border-[#c1a265] bg-[#16243d]";
            verdictTitle.textContent = "RECOMMENDED TO APPLY";
            verdictTitle.className = "text-lg font-bold tracking-wider uppercase text-[#c1a265]";
            verdictSubtitle.textContent = `High qualification alignment with ${(data.eligibility_confidence * 100).toFixed(1)}% model confidence.`;
        } else if (data.is_eligible) {
            verdictBanner.className = "p-6 rounded-lg border border-[#f59e0b] bg-[#2a2114]";
            verdictTitle.textContent = "POTENTIAL FIT (MODERATE)";
            verdictTitle.className = "text-lg font-bold tracking-wider uppercase text-[#f59e0b]";
            verdictSubtitle.textContent = `Candidate meets essential criteria but has minor experience gaps.`;
        } else {
            verdictBanner.className = "p-6 rounded-lg border border-[#f87171] bg-[#2d1519]";
            verdictTitle.textContent = "SKILL GAP DETECTED";
            verdictTitle.className = "text-lg font-bold tracking-wider uppercase text-[#f87171]";
            verdictSubtitle.textContent = `Candidate lacks fundamental required technologies for this role.`;
        }

        // 2. Fit Tier Badge (Marked Area: Green & White for Match, Lite Red & White for Not Match)
        fitTierBadge.textContent = data.fit_tier.toUpperCase();
        if (data.fit_tier === "Strong Match") {
            fitTierBadge.className = "px-3.5 py-1 text-xs font-bold uppercase rounded-full bg-[#16a34a] text-[#ffffff] shadow-sm";
        } else if (data.fit_tier === "Moderate Match") {
            fitTierBadge.className = "px-3.5 py-1 text-xs font-bold uppercase rounded-full bg-[#f59e0b] text-[#ffffff] shadow-sm";
        } else {
            // Not match (Skill Gap / Mismatched): Lite Red background with White text
            fitTierBadge.className = "px-3.5 py-1 text-xs font-bold uppercase rounded-full bg-[#ef4444] text-[#ffffff] shadow-sm";
        }

        // 3. Dealbreaker Indicator
        if (data.has_dealbreakers) {
            dealbreakerBadge.textContent = "CRITICAL DEALBREAKER DETECTED";
            dealbreakerBadge.className = "px-3 py-1 text-xs font-bold uppercase rounded-full bg-[#f87171] text-[#0d1726]";
        } else {
            dealbreakerBadge.textContent = "NO DEALBREAKERS DETECTED";
            dealbreakerBadge.className = "px-3 py-1 text-xs font-bold uppercase rounded-full bg-[#1e2f4a] text-[#c1a265]";
        }

        // 4. Match Score & Progress Bar
        scoreText.textContent = `${data.match_score.toFixed(1)} / 10.0`;
        const percentage = Math.min(Math.max((data.match_score / 10.0) * 100, 0), 100);
        scoreBar.style.width = `${percentage}%`;

        if (data.match_score >= 7.0) {
            scoreBar.className = "h-full bg-[#c1a265] transition-all duration-500";
        } else if (data.match_score >= 4.0) {
            scoreBar.className = "h-full bg-[#f59e0b] transition-all duration-500";
        } else {
            scoreBar.className = "h-full bg-[#f87171] transition-all duration-500";
        }

        // 5. System-1 Performance Metrics
        latencyMetric.textContent = `${data.latency_ms.toFixed(0)} ms (Roundtrip: ${clientLatencyMs} ms)`;
        tokenMetric.textContent = "$0.00 (0 Output Tokens)";

        // Unhide the results card
        resultsContainer.classList.remove("hidden");
        resultsContainer.scrollIntoView({ behavior: "smooth" });
    }

    /**
     * Triggers System-2 Deep Resume Audit via POST /api/deep-audit.
     */
    auditBtn.addEventListener("click", async () => {
        const jobDescription = jobInput.value.trim();
        const resumeContent = resumeInput.value.trim();

        auditBtn.disabled = true;
        auditSpinner.classList.remove("hidden");

        try {
            const response = await fetch("/api/deep-audit", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    job_description: jobDescription,
                    resume_content: resumeContent
                })
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || "Failed to generate deep audit.");
            }

            const auditData = await response.json();
            renderAuditResults(auditData);

        } catch (err) {
            showError(err.message);
        } finally {
            auditBtn.disabled = false;
            auditSpinner.classList.add("hidden");
        }
    });

    /**
     * Renders System-2 deep audit feedback lists.
     */
    function renderAuditResults(auditData) {
        missingSkillsList.innerHTML = "";
        redFlagsList.innerHTML = "";
        recommendationsList.innerHTML = "";

        // Render Missing Skills (White background with solid black text)
        if (auditData.missing_skills.length === 0) {
            missingSkillsList.innerHTML = `<li class="text-[#64748b] text-sm italic">No critical skills missing.</li>`;
        } else {
            auditData.missing_skills.forEach(skill => {
                const item = document.createElement("li");
                item.className = "text-sm text-[#0f172a] bg-[#ffffff] border border-[#d8d1c0] px-3.5 py-2.5 rounded-md font-medium shadow-sm";
                item.textContent = skill;
                missingSkillsList.appendChild(item);
            });
        }

        // Render Resume Red Flags (White background with lite red text)
        if (auditData.resume_red_flags.length === 0) {
            redFlagsList.innerHTML = `<li class="text-[#64748b] text-sm italic">No structural or technical red flags identified.</li>`;
        } else {
            auditData.resume_red_flags.forEach(flag => {
                const item = document.createElement("li");
                item.className = "text-sm text-[#ef4444] bg-[#ffffff] border border-[#fecaca] px-3.5 py-2.5 rounded-md font-medium shadow-sm";
                item.textContent = flag;
                redFlagsList.appendChild(item);
            });
        }

        // Render Actionable Recommendations (White background with solid black text)
        if (auditData.actionable_recommendations.length === 0) {
            recommendationsList.innerHTML = `<li class="text-[#64748b] text-sm italic">No specific improvements recommended.</li>`;
        } else {
            auditData.actionable_recommendations.forEach(rec => {
                const item = document.createElement("li");
                item.className = "text-sm text-[#0f172a] bg-[#ffffff] border border-[#d8d1c0] px-3.5 py-2.5 rounded-md font-medium shadow-sm";
                item.textContent = rec;
                recommendationsList.appendChild(item);
            });
        }

        auditContainer.classList.remove("hidden");
        auditContainer.scrollIntoView({ behavior: "smooth" });
    }
});
