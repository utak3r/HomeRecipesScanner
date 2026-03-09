import cv2
import numpy as np
import base64


"""
Base64 image encoding for sending to some endpoints
"""
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


"""
Light image preprocessing, used mostly for printed text.
It converts the image to grayscale, reduces noise and binarizes it.
"""
def light_image_preprocessing_for_ocr(image_path: str) -> np.ndarray:
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # noise reduction
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    # adaptive binarization
    thresh = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11, 2
    )

    return thresh

"""
Heavy image preprocessing, used mostly for handwritten text before OCR (or HTR)
It removes grid lines and enhances contrast.
"""
def heavy_image_preprocessing_for_ocr(image_path: str) -> np.ndarray:
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    thresh = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 41, 5)

    # grid detection
    scale = 40
    hor_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (img.shape[1] // scale, 1))
    ver_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, img.shape[0] // scale))
    mask_h = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, hor_kernel, iterations=1)
    mask_v = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, ver_kernel, iterations=1)
    grid_mask = cv2.add(mask_h, mask_v)

    # dilating the grid mask
    grid_mask = cv2.dilate(grid_mask, np.ones((5,5), np.uint8), iterations=1)

    # removing the grid by inpainting to not to destroy the letters themselves
    result_inpainted = cv2.inpaint(img, grid_mask, 3, cv2.INPAINT_TELEA)

    # CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    enhanced = clahe.apply(result_inpainted)

    return enhanced
