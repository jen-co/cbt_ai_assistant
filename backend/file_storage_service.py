import logging
from pathlib import Path
from werkzeug.utils import secure_filename
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class FileStorageService:
    """Service for handling file storage operations (images and text files)"""
    
    def __init__(self):
        """
        Initialize the file storage service
        """
    
    def validate_image_file(self, filename: str) -> bool:
        """
        Validate if a file is a valid image
        
        Args:
            filename: Name of the file to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not filename or '.' not in filename:
            return False
        
        extension = filename.rsplit('.', 1)[1].lower()
        return extension in {'png', 'jpg', 'jpeg'}
    
    def save_image_files(self, files: List, upload_dir: Path) -> Dict[str, Any]:
        """
        Save uploaded image files to the specified directory
        
        Args:
            files: List of uploaded files
            subdirectory: Subdirectory to save files in
            
        Returns:
            Dictionary containing success status, message, and saved files list
        """
        try:
            if not files:
                return {
                    "success": False,
                    "message": "No files provided",
                    "files": []
                }
            
            # Validate and save files
            saved_files = []
            
            for file in files:
                if not file.filename:
                    continue
                
                # Validate file type
                if not self.validate_image_file(file.filename):
                    continue
                
                # Secure the filename and save
                filename = secure_filename(file.filename)
                file_path = upload_dir / filename
                file.save(str(file_path))
                saved_files.append(filename)
            
            if not saved_files:
                return {
                    "success": False,
                    "message": "No valid images were uploaded",
                    "files": []
                }
            
            logger.info(f"Successfully uploaded {len(saved_files)} images to {upload_dir}")
            return {
                "success": True,
                "message": f"Successfully uploaded {len(saved_files)} images",
                "files": saved_files,
                "upload_directory": str(upload_dir)
            }
            
        except Exception as e:
            logger.error(f"Image upload failed: {str(e)}")
            return {
                "success": False,
                "message": f"Image upload failed: {str(e)}",
                "files": []
            }
    
    def save_text_file(self, text_content: str, file_path: str) -> Dict[str, Any]:
        """
        Save text content to a file
        
        Args:
            text_content: Text content to save
            file_path: File path to save the text to
            
        Returns:
            Dictionary containing success status, message
        """
        try:
            # Validate text content
            if not text_content or not text_content.strip():
                return {
                    "success": False,
                    "message": "Text content cannot be empty"
                }
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(text_content)
            
            logger.info(f"Successfully saved text to {file_path}")
            
            return {
                "success": True,
                "message": f"Text saved successfully to {file_path}",
                "text_length": len(text_content)
            }
            
        except Exception as e:
            logger.error(f"Text save failed: {str(e)}")
            return {
                "success": False,
                "message": f"Text save failed: {str(e)}"
            }
    
    