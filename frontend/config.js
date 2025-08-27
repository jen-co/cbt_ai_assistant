// Frontend configuration
const CONFIG = {
    // Backend API configuration
    API_BASE_URL: 'http://localhost:5000',
    
    // API endpoints
    ENDPOINTS: {
        ANALYSE: '/analyse',
        COGNITIVE_DISTORTIONS: '/cognitive-distortions',
        OCR: '/ocr',
        UPLOAD_IMAGES: '/upload-images',
        PROCESS_IMAGES: '/process-images',
        SAVE_TEXT: '/save-text',
        SAVE_ENTRY: '/save-entry'
    },
    
    // Application settings
    APP: {
        NAME: 'CBT Assistant',
        VERSION: '1.0.0'
    }
};

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CONFIG;
}
