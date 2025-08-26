// Track completed steps
let completedSteps = new Set();

// Store cognitive distortions data globally for use in challenge questions
let cognitiveDistortionsData = null;

let challengeQuestionsPopulated = false;

// Initialize the app
document.addEventListener('DOMContentLoaded', function() {
    // Load cognitive distortions from backend
    loadCognitiveDistortions();
    // Initialize step states
    updateStepStates();
});

// Load cognitive distortions from backend API
async function loadCognitiveDistortions() {
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}${CONFIG.ENDPOINTS.COGNITIVE_DISTORTIONS}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        // Store the data globally for use in challenge questions
        cognitiveDistortionsData = data.cognitive_distortions;
        populateDistortionList(cognitiveDistortionsData);
        
    } catch (error) {
        console.error('Failed to load cognitive distortions:', error);
        const distortionList = document.getElementById('distortion-list');
        distortionList.innerHTML = '<p class="error-message">Failed to load cognitive distortions. Please refresh the page to try again.</p>';
    }
}

// Populate the distortion list with data from backend
function populateDistortionList(distortions) {
    const distortionList = document.getElementById('distortion-list');
    
    if (!distortions || distortions.length === 0) {
        distortionList.innerHTML = '<p>No cognitive distortions available.</p>';
        return;
    }
    
    // Clear loading message
    distortionList.innerHTML = '';
    
    // Create distortion items
    distortions.forEach((distortion, index) => {
        const distortionId = distortion.name.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');
        const distortionItem = document.createElement('div');
        distortionItem.className = 'distortion-item';
        distortionItem.innerHTML = `
            <div class="distortion-header">
                <input type="checkbox" id="${distortionId}" value="${distortion.name}">
                <label for="${distortionId}">${distortion.name}</label>
                <button class="expand-btn" onclick="toggleDescription('${distortionId}')">▼</button>
            </div>
            <div class="distortion-description" id="${distortionId}-desc">
                <p>${distortion.description}</p>
            </div>
        `;
        distortionList.appendChild(distortionItem);
    });
}

// Toggle distortion description visibility
function toggleDescription(distortionId) {
    const description = document.getElementById(`${distortionId}-desc`);
    const expandBtn = description.previousElementSibling.querySelector('.expand-btn');
    
    if (description.classList.contains('expanded')) {
        description.classList.remove('expanded');
        expandBtn.classList.remove('expanded');
    } else {
        description.classList.add('expanded');
        expandBtn.classList.add('expanded');
    }
}

// Get selected cognitive distortions
function getSelectedDistortions() {
    const checkboxes = document.querySelectorAll('#step2 input[type="checkbox"]:checked');
    const selectedDistortions = [];
    
    for (let checkbox of checkboxes) {
        selectedDistortions.push(checkbox.value);
    }
    
    return selectedDistortions;
}

// Toggle step visibility
function toggleStep(stepNumber) {
    const step = document.getElementById(`step${stepNumber}`);
    const previousSteps = document.querySelectorAll(`.step:nth-of-type(${stepNumber - 1})`);
    
    if (previousSteps.length > 0) {
        const allPreviousStepsCompleted = Array.from(previousSteps).every(prevStep => 
            prevStep.classList.contains('completed')
        );
        if (allPreviousStepsCompleted) {
            step.classList.toggle('collapsed');
        } else {
            alert('Please complete all previous steps before proceeding.');
        }
    } else {
        step.classList.toggle('collapsed');
    }
}

// Complete a step and move to the next
function completeStep(stepNumber) {
    const currentStep = document.getElementById(`step${stepNumber}`);
    const nextStep = document.getElementById(`step${stepNumber + 1}`);
    
    // Mark current step as completed
    completedSteps.add(stepNumber);
    currentStep.classList.add('completed');
    
    // Collapse current step
    currentStep.classList.add('collapsed');
    
    // Update step states after completion
    updateStepStates();
    
    // Open next step if it exists
    if (nextStep) {
        if (stepNumber === 2 && !challengeQuestionsPopulated) {
            populateChallengeQuestions([])
        }
        nextStep.classList.remove('collapsed');      
        // Scroll to next step
        nextStep.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// Update step states based on completion
function updateStepStates() {
    const steps = document.querySelectorAll('.step');
    
    steps.forEach((step, index) => {
        const stepNumber = index + 1;
        
        if (stepNumber === 1) {
            // First step is always enabled
            step.classList.remove('disabled');
        } else {
            // Check if all previous steps are completed
            const allPreviousCompleted = Array.from({length: stepNumber - 1}, (_, i) => i + 1)
                .every(prevStepNum => completedSteps.has(prevStepNum));
            
            if (allPreviousCompleted) {
                step.classList.remove('disabled');
            } else {
                step.classList.add('disabled');
            }
        }
    });
}

// Submit the form
function submitForm() {
    const situationThoughts = document.getElementById('situation-thoughts').value.trim();
    
    if (!situationThoughts) {
        alert('Please complete Step 1 (Situation & Thoughts) before Saving.');
        return;
    }
    
    // Collect all form data
    const formData = {
        situationThoughts: document.getElementById('situation-thoughts').value,
        cognitiveDistortions: getSelectedDistortions(),
        challengeAnswers: getChallengeAnswers()
    };
    
    // Here you would typically send the data to your backend
    console.log('Form submitted with data:', formData);
    
    // Show success message
    showSuccessMessage();
    
    // Optionally reset the form
    // resetForm();
}

// Get challenge answers from Step 3
function getChallengeAnswers() {
    const challengeAnswers = {};
    const challengeItems = document.querySelectorAll('#challenge-list .distortion-item');
    
    challengeItems.forEach(item => {
        const distortionName = item.querySelector('label').textContent;
        const textareas = item.querySelectorAll('.challenge-answer');
        const answers = [];
        
        textareas.forEach(textarea => {
            answers.push(textarea.value.trim());
        });
        
        challengeAnswers[distortionName] = answers;
    });
    
    return challengeAnswers;
}

// Show success message
function showSuccessMessage() {
}

// Reset the form
function resetForm() {
    // Clear all textareas
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        textarea.value = '';
    });
    
    // Clear all checkboxes
    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        checkbox.checked = false;
    });
    
    // Collapse all distortion descriptions
    const descriptions = document.querySelectorAll('.distortion-description');
    descriptions.forEach(desc => {
        desc.classList.remove('expanded');
    });
    
    const expandBtns = document.querySelectorAll('.expand-btn');
    expandBtns.forEach(btn => {
        btn.classList.remove('expanded');
    });
    
    // Reset step states
    completedSteps.clear();
    
    // Remove completed and collapsed classes
    const steps = document.querySelectorAll('.step');
    steps.forEach(step => {
        step.classList.remove('completed', 'collapsed');
    });
    
    // Update step states after reset
    updateStepStates();
    
    // Remove success message
    const successMessage = document.querySelector('.success-message');
    if (successMessage) {
        successMessage.remove();
    }
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Run CBT Analysis
async function runCBTAnalysis(event, useContext) {
    
    const analysisBtn = event.currentTarget;
    const btnText = analysisBtn.querySelector('.btn-text');
    const loadingSpinner = analysisBtn.querySelector('.loading-spinner');
    
    // Validate that we have data to analyze
    const situationThoughts = document.getElementById('situation-thoughts').value.trim();
    
    if (!situationThoughts) {
        alert('Please complete Step 1 (Situation & Thoughts) before running the analysis.');
        return;
    }
    
    // Show loading state
    analysisBtn.disabled = true;
    btnText.style.display = 'none';
    loadingSpinner.style.display = 'flex';
    
    try {
        // Prepare data for API call
        const formData = {
            situationThoughts: situationThoughts
        };
        
        // Placeholder API call - replace with actual endpoint
        const response = await callCBTAnalysisAPI(formData, useContext);
        
        // Display results
       
        if (!useContext) { 
            displayAnalysisResults(response);
            populateChallengeQuestions(response.result.cognitive_distortions_issue);
            challengeQuestionsPopulated = true;
        }
        else {
            populateHistoricalComparison(response);
        }
        
        
    } catch (error) {
        console.error('Analysis failed:', error);
        alert('Analysis failed. Please try again.');
    } finally {
        // Reset button state
        analysisBtn.disabled = false;
        btnText.style.display = 'inline';
        loadingSpinner.style.display = 'none';
    }
}

// API call function to backend
async function callCBTAnalysisAPI(data, useContext) {
    try {
        // Use the combined situation and thoughts directly as the question
        const question = data.situationThoughts;
        
        const response = await fetch(`${CONFIG.API_BASE_URL}${CONFIG.ENDPOINTS.ANALYSE}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                question: question,
                use_context: useContext
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        console.log(result);
        return result; 
        
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

// Display analysis results
function displayAnalysisResults(response) {
    console.log(response);
    const analysisResults = document.getElementById('analysis-results');
    const aiDistortionList = document.getElementById('ai-distortion-list');
    
    // Clear previous results
    aiDistortionList.innerHTML = '';
    
    // Use cognitive_distortions_issue array from the response
    const distortions = response.result.cognitive_distortions_issue || [];
    
    if (distortions.length > 0) {
        distortions.forEach((distortion, index) => {
            const distortionId = `ai-${distortion.name.toLowerCase().replace(/\s+/g, '-')}-${index}`;
            const distortionItem = document.createElement('div');
            distortionItem.className = 'distortion-item';
            distortionItem.innerHTML = `
                <div class="distortion-header">
                    <label>${distortion.name}</label>
                    <button class="expand-btn" onclick="toggleDescription('${distortionId}')">▼</button>
                </div>
                <div class="distortion-description expanded" id="${distortionId}-desc">
                    <p>${distortion.explanation}</p>
                </div>
            `;
            aiDistortionList.appendChild(distortionItem);
        });
    } else {
        aiDistortionList.innerHTML = '<p>No cognitive distortions were identified in your thoughts.</p>';
    }
    
    // Show results section
    analysisResults.style.display = 'block';
    
    // Scroll to results
    analysisResults.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Populate challenge questions for Step 3
function populateChallengeQuestions(apiDistortions) {
    const challengeList = document.getElementById('challenge-list');
    challengeList.innerHTML = '';
    
    // Get manually selected distortions from checkboxes
    const selectedDistortions = getSelectedDistortions();
    
    const aiDistortionNames = apiDistortions.map(distortion => distortion.name);
    
    // Create a map of all available distortions and their questions
    const allDistortionsMap = {};
    if (cognitiveDistortionsData) {
        cognitiveDistortionsData.forEach(distortion => {
            allDistortionsMap[distortion.name] = distortion.questions || [];
        });
    }
    
    // Combine AI-detected distortions with manually selected ones that aren't already in AI results
    const distortionsToChallenge = [...apiDistortions];
    
    // Add manually selected distortions that aren't already in AI results
    selectedDistortions.forEach(selectedDistortionName => {
        if (!aiDistortionNames.includes(selectedDistortionName)) {
            // Find the distortion data from the global cognitive distortions data
            const distortionData = cognitiveDistortionsData?.find(d => d.name === selectedDistortionName);
            if (distortionData) {
                distortionsToChallenge.push({
                    name: distortionData.name,
                    questions: distortionData.questions || []
                });
            }
        }
    });
    
    if (distortionsToChallenge.length === 0) {
        challengeList.innerHTML = '<p>No cognitive distortions to challenge. Please run the AI analysis in Step 2 first or select distortions manually.</p>';
        return;
    }
    
    // Create challenge items for all distortions to challenge
    distortionsToChallenge.forEach((distortion, index) => {
        const distortionId = `challenge-${distortion.name.toLowerCase().replace(/\s+/g, '-')}-${index}`;
        const questions = distortion.questions || [];
        
        const challengeItem = document.createElement('div');
        challengeItem.className = 'distortion-item';
        challengeItem.innerHTML = `
            <div class="distortion-header">
                <label>${distortion.name}</label>
                <button class="expand-btn" onclick="toggleDescription('${distortionId}')">▼</button>
            </div>
            <div class="distortion-description expanded" id="${distortionId}-desc">
                <div class="challenge-questions">
                    ${questions.map(question => `
                        <div class="question-item">
                            <p class="question-text">${question}</p>
                            <textarea class="challenge-answer" placeholder="Write your answer here..." rows="3"></textarea>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        challengeList.appendChild(challengeItem);
    });
}

// Populate historical comparison for Step 4
function populateHistoricalComparison(response) {
    const historicalList = document.getElementById('historical-distortions-list');
    const commonThemesTextarea = document.getElementById('common-themes');
    const pastEntriesTextarea = document.getElementById('past-entries');
    
    historicalList.innerHTML = '';
    
    console.log(response);
    
    // Get the historical distortions from the API response
    const historicalDistortions = response?.result?.cognitive_distortions_context || [];
    const comparisonText = response?.result.comparison || "No comparison data available.";
    const sourceContent = response?.source_content || "No past entries available.";
    
    // Populate historical distortions
    if (historicalDistortions.length > 0) {
        historicalDistortions.forEach((distortion, index) => {
            const distortionId = `historical-${distortion.name.toLowerCase().replace(/\s+/g, '-')}-${index}`;
            const distortionItem = document.createElement('div');
            distortionItem.className = 'distortion-item';
            distortionItem.innerHTML = `
                <div class="distortion-header">
                    <label>${distortion.name}</label>
                    <button class="expand-btn" onclick="toggleDescription('${distortionId}')">▼</button>
                </div>
                <div class="distortion-description expanded" id="${distortionId}-desc">
                    <p>${distortion.explanation}</p>
                </div>
            `;
            historicalList.appendChild(distortionItem);
        });
    } else {
        historicalList.innerHTML = '<p>No historical cognitive distortion patterns found.</p>';
    }
    
    // Populate common themes
    commonThemesTextarea.value = comparisonText;
    pastEntriesTextarea.value = sourceContent;

}

// Add keyboard shortcuts
document.addEventListener('keydown', function(event) {
    // Ctrl/Cmd + Enter to submit form
    if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
        event.preventDefault();
        submitForm();
    }
    
    // Tab to navigate between steps
    if (event.key === 'Tab') {
        // Allow normal tab behavior
        return;
    }
}); 