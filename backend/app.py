from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import traceback
import sys
import json
import os
from pathlib import Path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from backend.config import Config
from backend.cbt_llm_service import CBTLLMService
from backend.ocr_service import OCRService
from backend.file_storage_service import FileStorageService
from backend.models import AnalysisRequest, AnalysisResponse, ErrorResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app(config: Config = None) -> Flask:
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Use provided config or create default
    if config is None:
        config = Config()
    
    app.config.from_object(config)
    
    # Setup CORS
    CORS(app, origins=config.CORS_ORIGINS)
    
    # todo work out why cursor made rag_service a property of the app object?
    # Initialize LLM service
    try:
        llm_service = CBTLLMService(config)
        app.llm_service = llm_service
        logger.info("LLM service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize LLM service: {str(e)}")
        app.llm_service = None

    file_storage = FileStorageService()    

    
    @app.route('/analyse', methods=['POST'])
    def analyse_question():
        """Analyse a user's question for cognitive distortions"""
        try: 
            logger.info(f"Request method: {request.method}")
            logger.info(f"Request headers: {dict(request.headers)}")
            logger.info(f"Request data: {request.get_data()}")
            
            # Validate request
            if not request.is_json:
                return jsonify(ErrorResponse(
                    message="Content-Type must be application/json"
                ).model_dump()), 400
            
            # Parse request
            try:
                request_data = request.get_json()
                logger.info(f"Request JSON: {request_data}")
                analysis_request = AnalysisRequest(**request_data)
            except Exception as e:
                logger.info(f"Error: {e}")
                return jsonify(ErrorResponse(
                    message=f"Invalid request format: {str(e)}"
                ).model_dump()), 400
            
            # Validate question
            if not analysis_request.question or not analysis_request.question.strip():
                return jsonify(ErrorResponse(
                    message="Question cannot be empty"
                ).model_dump()), 400
            
            # Check if LLM service is available
            if not app.llm_service:
                return jsonify(ErrorResponse(
                    message="LLM service not available"
                ).model_dump()), 503
            
            # Perform analysis
            logger.info(f"Processing analysis request: {analysis_request.question[:100]}...")
            # Optional use_context flag in request; default handled by model
            use_context = getattr(analysis_request, 'use_context', True)
            analysis_result, source_content = app.llm_service.analyse_question(analysis_request.question, use_context=use_context)
            
            # Return response
            response = AnalysisResponse(result=analysis_result, source_content=source_content)
            return jsonify(response.model_dump()), 200
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify(ErrorResponse(
                message=f"Analysis failed: {str(e)}"
            ).model_dump()), 500

    
    @app.route('/cognitive-distortions', methods=['GET'])
    def get_cognitive_distortions():
        """Get all cognitive distortions from the JSON file"""
        try:
            # Get the path to the cognitive_distortions.json file
            json_file_path = config.COGNITIVE_DISTORTIONS_PATH
            
            # Check if file exists
            if not os.path.exists(json_file_path):
                logger.error(f"Cognitive distortions file not found: {json_file_path}")
                return jsonify(ErrorResponse(
                    message="Cognitive distortions data not available"
                ).model_dump()), 404
            
            # Read and parse the JSON file
            with open(json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            logger.info("Successfully retrieved cognitive distortions")
            return jsonify(data), 200
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing cognitive distortions JSON: {str(e)}")
            return jsonify(ErrorResponse(
                message="Error parsing cognitive distortions data"
            ).model_dump()), 500
        except Exception as e:
            logger.error(f"Error retrieving cognitive distortions: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify(ErrorResponse(
                message=f"Error retrieving cognitive distortions: {str(e)}"
            ).model_dump()), 500

    
    @app.route('/upload-images', methods=['POST'])
    def upload_images():
        """Upload multiple images to journal_entries_photos directory"""
        try:
            # Check if files are present in request
            if 'images' not in request.files:
                return jsonify(ErrorResponse(
                    message="No images provided"
                ).model_dump()), 400
            
            files = request.files.getlist('images')
            
            if not files or all(file.filename == '' for file in files):
                return jsonify(ErrorResponse(
                    message="No images selected"
                ).model_dump()), 400

            # Save image files
            result = file_storage.save_image_files(files, config.JOURNAL_IMAGES_PATH)
            
            if not result["success"]:
                return jsonify(ErrorResponse(
                    message=result["message"]
                ).model_dump()), 400
            
            return jsonify({
                "success": True,
                "message": result["message"],
                "files": result["files"]
            }), 200
            
        except Exception as e:
            logger.error(f"Image upload failed: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify(ErrorResponse(
                message=f"Image upload failed: {str(e)}"
            ).model_dump()), 500
    
    @app.route('/process-images', methods=['POST'])
    def process_images():
        """Process images in journal_entries_photos directory and convert to text"""
        try:
            # Initialize OCR service
            ocr_service = OCRService(config)
            
            # Process images and extract text
            full_text = ocr_service.process_images()
            
            return jsonify({
                "success": True,
                "message": f"Successfully processed images",
                "text_length": len(full_text),
                "extracted_text": full_text
            }), 200
            
        except FileNotFoundError as e:
            logger.error(f"Images directory or files not found: {str(e)}")
            return jsonify(ErrorResponse(
                message=str(e)
            ).model_dump()), 404
            
        except Exception as e:
            logger.error(f"Image processing failed: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify(ErrorResponse(
                message=f"Image processing failed: {str(e)}"
            ).model_dump()), 500
    
    @app.route('/save-text', methods=['POST'])
    def save_text():
        """Save extracted text to a txt file"""
        try:
            # Validate request
            if not request.is_json:
                return jsonify(ErrorResponse(
                    message="Content-Type must be application/json"
                ).model_dump()), 400
            
            # Parse request
            try:
                request_data = request.get_json()
                text_content = request_data.get('text', '')
            except Exception as e:
                return jsonify(ErrorResponse(
                    message=f"Invalid request format: {str(e)}"
                ).model_dump()), 400
            
            result = file_storage.save_text_file(text_content, config.FULL_JOURNAL_TEXT_PATH)
            
            if not result["success"]:
                return jsonify(ErrorResponse(
                    message=result["message"]
                ).model_dump()), 400
            
            return jsonify({
                "success": True,
                "message": result["message"],
                "text_length": result["text_length"]
            }), 200
            
        except Exception as e:
            logger.error(f"Text save failed: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify(ErrorResponse(
                message=f"Text save failed: {str(e)}"
            ).model_dump()), 500


    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors"""
        return jsonify(ErrorResponse(
            message="Endpoint not found"
        ).model_dump()), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 errors"""
        return jsonify(ErrorResponse(
            message="Method not allowed"
        ).model_dump()), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        logger.error(f"Internal server error: {str(error)}")
        return jsonify(ErrorResponse(
            message="Internal server error"
        ).model_dump()), 500
    
    return app

def run_app(config: Config = None, host: str = None, port: int = None, debug: bool = None):
    """Run the Flask application"""
    app = create_app(config)
    
    # Override config with function parameters if provided
    if config is None:
        config = Config()
    
    run_host = host or config.API_HOST
    run_port = port or config.API_PORT
    run_debug = debug if debug is not None else config.DEBUG
    
    logger.info(f"Starting CBT Assistant API on {run_host}:{run_port}")
    app.run(host=run_host, port=run_port, debug=run_debug)

if __name__ == '__main__':
    run_app(debug=True) 