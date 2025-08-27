import logging
from pathlib import Path
from ollama import generate, Options
import cv2
import numpy as np

logger = logging.getLogger(__name__)

class OCRService:
    """Service for processing images and extracting text using OCR"""
    
    def __init__(self, config=None):
        """
        Initialize the OCR service
        
        Args:
            images_dir: Path to the directory containing images to process
            config: Configuration object containing OCR settings
        """
        self.config = config
        self.images_dir = self.config.JOURNAL_IMAGES_PATH
        self.prompt = "Perform Optical Character Recognition (OCR) on the following image. The output should be the extracted text"
        self.options = Options(
            num_predict=300,
            repeat_penalty=2,
        )
        
        # Create splits directory if it doesn't exist
        if self.images_dir:
            self._ensure_splits_directory()
    
    def _ensure_splits_directory(self):
        """Ensure the splits directory exists"""
        if self.images_dir:
            splits_dir = self.images_dir / "splits"
            splits_dir.mkdir(exist_ok=True)
            logger.info(f"Ensured splits directory exists: {splits_dir}")
    
    def set_images_directory(self, images_dir: Path):
        """Set the images directory path"""
        self.images_dir = images_dir
        # Create splits directory if it doesn't exist
        if self.images_dir:
            self._ensure_splits_directory()
    
    def get_image_files(self):
        """Get all image files from the images directory"""
        if not self.images_dir or not self.images_dir.exists():
            raise FileNotFoundError(f"Images directory not found: {self.images_dir}")
        
        image_files = []
        for ext in ['*.jpeg', '*.jpg', '*.png']:
            image_files.extend(self.images_dir.glob(ext))
        
        if not image_files:
            raise FileNotFoundError(f"No image files found in directory: {self.images_dir}")
        
        return image_files
    
    def process_single_image(self, image_file: Path) -> str:
        """
        Process a single image and extract text
        
        Args:
            image_file: Path to the image file
            
        Returns:
            Extracted text from the image
        """
        try:
            logger.info(f"Processing image: {image_file.name}")
            left_part, right_part = self.split_image(image_file)
            # Use Ollama to perform OCR
            model = self.config.OCR_LLM_MODEL if self.config else 'qwen2.5vl:7b'
            result_left = generate(model, self.prompt, images=[str(left_part)], options=self.options)
            result_right = generate(model, self.prompt, images=[str(right_part)], options=self.options)
            extracted_text = result_left.response.strip() + result_right.response.strip()
            
            if extracted_text:
                return f"\n\n--- {image_file.name} ---\n{extracted_text}"
            else:
                return f"\n\n--- {image_file.name} ---\n[No text extracted]"
                
        except Exception as e:
            logger.error(f"Failed to process {image_file.name}: {str(e)}")
            return f"\n\n--- {image_file.name} ---\n[OCR processing failed: {str(e)}]"

    def split_image(self, image_file: Path) -> str:
        """
        Split the image into left and right parts
        """
        image = cv2.imread(image_file)
        image = cv2.resize(image, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_LINEAR)
        # Convert image to grayscale
        gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        gray = cv2.bitwise_not(gray)
        bw = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, -2)
        vertical = np.copy(bw)
        rows = vertical.shape[0]
        cols = vertical.shape[1]
        verticalsize = rows // 15
        verticalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (1, verticalsize))
        vertical = cv2.erode(vertical, verticalStructure)
        vertical = cv2.dilate(vertical, verticalStructure)
        # add border of 200 pixels on the left and right
        vertical[:, :200] = 0
        vertical[:, cols-200:]  = 0
        
        #get all the cols that are white
        (rows, cols) = np.where(vertical != 0)
        avg_col = int(np.round(np.average(cols)))
        print(avg_col)

        left_part = image[:, :avg_col] 
        right_part = image[:, avg_col:]  

        # Ensure splits directory exists
        self._ensure_splits_directory()
        
        # Create file paths for left and right parts. We save it for debugging purposes. TODO maybe just pass the bytes to the ocr model
        splits_dir = self.images_dir / "splits"
        file_left = splits_dir / f"{image_file.stem}_left{image_file.suffix}"
        file_right = splits_dir / f"{image_file.stem}_right{image_file.suffix}"
        
        # Save the split images
        cv2.imwrite(str(file_left), left_part)
        cv2.imwrite(str(file_right), right_part)
        
        logger.info(f"Split image {image_file.name} into {file_left.name} and {file_right.name}")
        return file_left, file_right
    
    def process_images(self) -> str:
        """
        Process all images in the images directory and extract text
        
        Returns:
            Combined text from all processed images
        """
        try:
            # Get all image files
            image_files = self.get_image_files()
            logger.info(f"Found {len(image_files)} images to process")
            
            # Process each image and extract text
            full_text = ""
            
            for image_file in image_files:
                extracted_text = self.process_single_image(image_file)
                # Remove newlines from extracted text
                cleaned_text = extracted_text.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
                full_text += cleaned_text
            
            logger.info(f"Successfully processed {len(image_files)} images")
            return full_text
            
        except Exception as e:
            logger.error(f"Image processing failed: {str(e)}")
            raise
