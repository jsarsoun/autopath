import cv2
import numpy as np
import pytesseract
import os

def parse_image(image_path):
    try:
        # Set the path to the Tesseract executable
        tesseract_path = os.environ.get('TESSERACT_PATH', r'C:\Program Files\Tesseract-OCR\tesseract.exe')
        pytesseract.pytesseract.tesseract_cmd = tesseract_path

        # Read the image
        img = cv2.imread(image_path)
        if img is None:
            return [{'error': f'Failed to read the image file: {image_path}'}]

        # Get image dimensions
        height, width = img.shape[:2]

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Apply thresholding
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)

        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Extract data from each bar
        data = []
        for i, contour in enumerate(contours):
            x, y, w, h = cv2.boundingRect(contour)
            if h > height * 0.05 and w > width * 0.01:  # Adjust thresholds as needed
                # Extract the region containing the team number
                team_number_region = gray[y:y+h, x:x+w]
                
                # Use Tesseract to recognize the team number
                team_number = pytesseract.image_to_string(team_number_region, config='--psm 7 -c tessedit_char_whitelist=0123456789')
                team_number = ''.join(filter(str.isdigit, team_number))
                
                # Save the preprocessed image for debugging
                cv2.imwrite(os.path.join(os.path.dirname(image_path), f'debug_team_number_{i+1}.png'), team_number_region)
                
                if team_number:
                    print(f"Bar {i+1} - Recognized team number: {team_number}")
                    data.append({
                        'team_number': int(team_number),
                    })
                else:
                    print(f"Bar {i+1} - No team number recognized")

        if not data:
            return [{'error': 'No valid data found in the image.', 'details': 'The image processing completed, but no valid data was extracted. Check if the image is clear and contains the expected format.'}]

        return data

    except pytesseract.pytesseract.TesseractNotFoundError:
        return [{'error': 'Tesseract is not installed or the path is incorrect.', 'details': 'Please install Tesseract OCR and set the TESSERACT_PATH environment variable.'}]
    except cv2.error as e:
        return [{'error': 'Error processing the image with OpenCV', 'details': str(e)}]
    except Exception as e:
        return [{'error': 'An unexpected error occurred while processing the image', 'details': str(e)}]

# Example usage:
# data = parse_image('path/to/your/image.png')
# print(data)
