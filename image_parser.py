import cv2
import numpy as np
import pytesseract
from PIL import Image

def parse_image(image_path):
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
    
    return data

# Example usage:
# data = parse_image('c:\\Users\\jsars\\Programming\\autopath\\newplot.png')
# print(data)
