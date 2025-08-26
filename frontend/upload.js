// Global variables
let uploadedFiles = [];
let ocrResults = [];

// Initialize the app
document.addEventListener('DOMContentLoaded', function() {
    setupFileUpload();
});

// Setup file upload functionality
function setupFileUpload() {
    const fileInput = document.getElementById('image-upload');
    const uploadedImagesContainer = document.getElementById('uploaded-images');
    const processBtn = document.getElementById('process-btn');

    fileInput.addEventListener('change', function(event) {
        const files = Array.from(event.target.files);
        
        if (files.length === 0) {
            uploadedFiles = [];
            uploadedImagesContainer.innerHTML = '';
            processBtn.disabled = true;
            return;
        }

        // Validate file types
        const validTypes = ['image/jpeg', 'image/jpg', 'image/png'];
        const invalidFiles = files.filter(file => !validTypes.includes(file.type));
        
        if (invalidFiles.length > 0) {
            alert('Please select only JPG, JPEG, or PNG files.');
            return;
        }

        uploadedFiles = files;
        displayImagePreviews(files);
        processBtn.disabled = false;
    });
}

// Display image previews
function displayImagePreviews(files) {
    const container = document.getElementById('uploaded-images');
    container.innerHTML = '';

    files.forEach((file, index) => {
        const reader = new FileReader();
        reader.onload = function(e) {
            const imageDiv = document.createElement('div');
            imageDiv.className = 'image-preview';
            imageDiv.innerHTML = `
                <img src="${e.target.result}" alt="Preview ${index + 1}">
                <div class="image-info">
                    <span class="image-name">${file.name}</span>
                    <span class="image-size">${formatFileSize(file.size)}</span>
                </div>
            `;
            container.appendChild(imageDiv);
        };
        reader.readAsDataURL(file);
    });
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Process images with OCR
async function processImages() {
    if (uploadedFiles.length === 0) {
        alert('Please select images to process.');
        return;
    }

    const processBtn = document.getElementById('process-btn');
    const btnText = processBtn.querySelector('.btn-text');
    const loadingSpinner = document.getElementById('ocr-loading-spinner');

    // Show loading state
    processBtn.disabled = true;
    btnText.style.display = 'none';
    loadingSpinner.style.display = 'flex';

    try {
        // Create FormData for file upload
        const formData = new FormData();
        uploadedFiles.forEach((file, index) => {
            formData.append('images', file);
        });

        // First upload images
        const uploadResponse = await fetch(`${CONFIG.API_BASE_URL}${CONFIG.ENDPOINTS.UPLOAD_IMAGES}`, {
            method: 'POST',
            body: formData
        });

        if (!uploadResponse.ok) {
            const errorData = await uploadResponse.json();
            throw new Error(errorData.message || `Upload failed! status: ${uploadResponse.status}`);
        }

        const uploadResult = await uploadResponse.json();
        
        // Then process images with OCR
        const response = await fetch(`${CONFIG.API_BASE_URL}${CONFIG.ENDPOINTS.PROCESS_IMAGES}`, {
            method: 'POST'
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        
        // Display results
        displayOCRResults(result.extracted_text || '');
        
        // Show results step
        document.getElementById('results-step').classList.remove('collapsed');
        document.getElementById('results-step').scrollIntoView({ behavior: 'smooth', block: 'start' });

    } catch (error) {
        console.error('OCR processing failed:', error);
        alert('OCR processing failed. Please try again.');
    } finally {
        // Reset button state
        processBtn.disabled = false;
        btnText.style.display = 'inline';
        loadingSpinner.style.display = 'none';
    }
}

// Display OCR results
function displayOCRResults(text) {
    const textarea = document.getElementById('ocr-text');
    textarea.value = text;
}

// Edit text functionality
function editText() {
    const textarea = document.getElementById('ocr-text');
    textarea.readOnly = false;
    textarea.focus();
    
    // Change button text
    const editBtn = document.querySelector('.secondary-btn');
    editBtn.textContent = 'Done Editing';
    editBtn.onclick = function() {
        textarea.readOnly = true;
        editBtn.textContent = 'Edit Text';
        editBtn.onclick = editText;
    };
}

// Save to database
async function saveToDatabase() {
    const textarea = document.getElementById('ocr-text');
    const text = textarea.value.trim();
    
    if (!text) {
        alert('Please ensure there is text to save.');
        return;
    }

    const saveBtn = document.getElementById('save-btn');
    const btnText = saveBtn.querySelector('.btn-text');
    const loadingSpinner = document.getElementById('save-loading-spinner');

    // Show loading state
    saveBtn.disabled = true;
    btnText.style.display = 'none';
    loadingSpinner.style.display = 'flex';

    try {
        // Send text to save endpoint
        const response = await fetch(`${CONFIG.API_BASE_URL}${CONFIG.ENDPOINTS.SAVE_TEXT}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: text
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        console.log('Text saved successfully:', result);

        // Show success message
        showSuccessMessage();

    } catch (error) {
        console.error('Save failed:', error);
        alert('Failed to save to database. Please try again.');
    } finally {
        // Reset button state
        saveBtn.disabled = false;
        btnText.style.display = 'inline';
        loadingSpinner.style.display = 'none';
    }
}

// Show success message
function showSuccessMessage() {
    const successMessage = document.getElementById('success-message');
    const formContainer = document.querySelector('.form-container');
    
    formContainer.style.display = 'none';
    successMessage.style.display = 'block';
}

// Reset form
function resetForm() {
    // Clear file input
    document.getElementById('image-upload').value = '';
    
    // Clear previews
    document.getElementById('uploaded-images').innerHTML = '';
    
    // Clear OCR results
    document.getElementById('ocr-text').value = '';
    
    // Reset buttons
    document.getElementById('process-btn').disabled = true;
    
    // Hide results step
    document.getElementById('results-step').classList.add('collapsed');
    
    // Show form container
    document.querySelector('.form-container').style.display = 'block';
    document.getElementById('success-message').style.display = 'none';
    
    // Reset global variables
    uploadedFiles = [];
    ocrResults = [];
}

// Toggle step visibility
function toggleStep(stepName) {
    const step = document.getElementById(`${stepName}-step`);
    step.classList.toggle('collapsed');
}
