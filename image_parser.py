import cv2
import numpy as np
from PIL import Image
import os

def parse_image(image_path):
    try:
        import pytesseract
        # Set the path to the Tesseract executable
        tesseract_path = os.environ.get('TESSERACT_PATH', r'C:\Program Files\Tesseract-OCR\tesseract.exe')
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
    except ImportError:
        return [{'error': 'Pytesseract is not installed. Please install it using pip install pytesseract.'}]

    try:
        # Read the image
        img = cv2.imread(image_path)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Threshold the image
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        
        # Perform text extraction
        text = pytesseract.image_to_string(Image.fromarray(thresh))
        
        # Parse the text to extract x, y values and categories
        lines = text.split('\n')
        data = []
        for line in lines:
            parts = line.split()
            if len(parts) == 3:
                try:
                    x = float(parts[0])
                    y = float(parts[1])
                    category = parts[2]
                    data.append({'x': x, 'y': y, 'category': category})
                except ValueError:
                    continue
        
        return data if data else [{'error': 'No valid data found in the image.'}]
    except pytesseract.pytesseract.TesseractNotFoundError:
        return [{'error': 'Tesseract is not installed or the path is incorrect. Please install Tesseract OCR and set the TESSERACT_PATH environment variable.'}]
    except Exception as e:
        return [{'error': f'An error occurred while processing the image: {str(e)}'}]

# Example usage:
# data = parse_image('c:\\Users\\jsars\\Programming\\autopath\\newplot.png')
# print(data)
