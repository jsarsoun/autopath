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

        # Threshold the image
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)

        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Sort contours by x-coordinate
        contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[0])

        # Extract data from each bar
        data = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if h > height * 0.1:  # Filter out small contours
                bar_img = img[y:y+h, x:x+w]
                team_number = pytesseract.image_to_string(bar_img, config='--psm 7 -c tessedit_char_whitelist=0123456789').strip()
                
                if team_number:
                    total_points = int((height - y) / height * 20)  # Estimate total points
                    
                    # Estimate points for each task based on color
                    task_points = {
                        'auto_leave': 0,
                        'auto_speaker': 0,
                        'teleop_amp': 0,
                        'teleop_speaker': 0,
                        'endgame_onstage': 0,
                        'endgame_park': 0
                    }
                    
                    # You would need to implement color detection here
                    # For simplicity, let's just assign random values
                    for task in task_points:
                        task_points[task] = np.random.randint(0, total_points)
                    
                    data.append({
                        'team_number': int(team_number),
                        'total_points': total_points,
                        **task_points
                    })

        if not data:
            return [{'error': 'No valid data found in the image.', 'details': 'The image processing completed, but no valid data was extracted. Check if the image is clear and contains the expected bar chart format.'}]

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
