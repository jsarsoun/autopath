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

        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Sort contours by x-coordinate
        contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[0])

        # Extract data from each bar
        data = []
        for i, contour in enumerate(contours):
            x, y, w, h = cv2.boundingRect(contour)
            if h > height * 0.5 and w > width * 0.05:  # Adjust thresholds as needed
                # Extract the entire bar
                bar_region = img[y:y+h, x:x+w]
                
                # Focus on the bottom part of the bar for team number
                team_number_region = bar_region[int(h*0.8):, :]
                
                # Preprocess the team number region
                team_number_gray = cv2.cvtColor(team_number_region, cv2.COLOR_BGR2GRAY)
                team_number_thresh = cv2.threshold(team_number_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
                
                # Use Tesseract to recognize the team number
                team_number = pytesseract.image_to_string(team_number_thresh, config='--psm 7 -c tessedit_char_whitelist=0123456789')
                team_number = ''.join(filter(str.isdigit, team_number))
                
                # Save the preprocessed image for debugging
                cv2.imwrite(os.path.join(os.path.dirname(image_path), f'debug_team_number_bar_{i+1}.png'), team_number_thresh)
                
                if team_number:
                    print(f"Bar {i+1} - Recognized team number: {team_number}")
                    total_points = int((height - y) / height * 100)  # Estimate total points
                    
                    # Estimate points for each task based on color
                    task_points = {
                        'auto_leave': 0,
                        'auto_speaker': 0,
                        'teleop_amp': 0,
                        'teleop_speaker': 0,
                        'endgame_onstage': 0,
                        'endgame_park': 0
                    }
                    
                    # Define color ranges (in HSV)
                    colors = {
                        'auto_leave': ([0, 100, 100], [10, 255, 255]),  # Red
                        'auto_speaker': ([110, 100, 100], [130, 255, 255]),  # Blue
                        'teleop_amp': ([50, 100, 100], [70, 255, 255]),  # Green
                        'teleop_speaker': ([20, 100, 100], [40, 255, 255]),  # Yellow
                        'endgame_onstage': ([130, 100, 100], [150, 255, 255]),  # Purple
                        'endgame_park': ([160, 100, 100], [180, 255, 255])  # Pink
                    }
                    
                    # Convert bar region to HSV
                    hsv = cv2.cvtColor(bar_region, cv2.COLOR_BGR2HSV)
                    
                    for task, (lower, upper) in colors.items():
                        mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
                        task_height = np.sum(mask > 0) // w  # Calculate height of color segment
                        task_points[task] = int(task_height / h * total_points)
                    
                    data.append({
                        'team_number': int(team_number),
                        'total_points': total_points,
                        **task_points
                    })
                else:
                    print(f"Bar {i+1} - No team number recognized")

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
