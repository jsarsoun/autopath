import cv2
import numpy as np
from PIL import Image
import os
import pytesseract

def parse_image(image_path):
    try:
        # Set the path to the Tesseract executable
        tesseract_path = os.environ.get('TESSERACT_PATH', r'C:\Program Files\Tesseract-OCR\tesseract.exe')
        pytesseract.pytesseract.tesseract_cmd = tesseract_path

        # Read the image
        img = cv2.imread(image_path)
        if img is None:
            return [{'error': f'Failed to read the image file: {image_path}'}]

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Apply different preprocessing techniques
        preprocessed_images = [
            gray,
            cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1],
            cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        ]

        all_data = []
        for i, thresh in enumerate(preprocessed_images):
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

            all_data.extend(data)

        if not all_data:
            return [{'error': 'No valid data found in the image. Please ensure the image contains text in the format: x y category'}]

        return all_data

    except pytesseract.pytesseract.TesseractNotFoundError:
        return [{'error': 'Tesseract is not installed or the path is incorrect. Please install Tesseract OCR and set the TESSERACT_PATH environment variable.'}]
    except Exception as e:
        return [{'error': f'An error occurred while processing the image: {str(e)}'}]

# Example usage:
# data = parse_image('path/to/your/image.png')
# print(data)
