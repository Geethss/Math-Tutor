import cv2
import numpy as np
import os

def load_gray(path):
    img = cv2.imread(path)
    if img is None:
        raise ValueError(f"Could not load image from path: {path}")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return img, gray

def deskew(gray):
    coords = np.column_stack(np.where(gray < 255))
    if len(coords) == 0:
        return gray
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = 90 + angle
    (h, w) = gray.shape
    M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
    return cv2.warpAffine(gray, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

def find_blocks(gray, min_area=1500):
    print(f"[DEBUG] Finding blocks in image of shape: {gray.shape}")
    _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
    dil = cv2.dilate(th, kernel, iterations=1)
    contours, _ = cv2.findContours(dil, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print(f"[DEBUG] Found {len(contours)} contours")
    boxes = []
    for i, c in enumerate(contours):
        x, y, w, h = cv2.boundingRect(c)
        area = w * h
        print(f"[DEBUG] Contour {i}: area={area}, min_area={min_area}")
        if area > min_area:
            boxes.append((x, y, w, h))
            print(f"[DEBUG] Added box: ({x}, {y}, {w}, {h})")
    boxes = sorted(boxes, key=lambda b: b[1])
    print(f"[DEBUG] Final boxes: {boxes}")
    return boxes

def crop_blocks(image_path, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    try:
        img, gray = load_gray(image_path)
        gray = deskew(gray)
        boxes = find_blocks(gray)
        crops = []
        print(f"[DEBUG] Found {len(boxes)} blocks in image")
        for i, (x, y, w, h) in enumerate(boxes, start=1):
            pad = 5
            crop = img[y - pad:y + h + pad, x - pad:x + w + pad]
            print(f"[DEBUG] Block {i}: crop shape = {crop.shape}")
            
            # Check if crop is empty
            if crop.size == 0 or crop.shape[0] == 0 or crop.shape[1] == 0:
                print(f"[DEBUG] Block {i} is empty, skipping")
                continue
                
            fname = os.path.join(out_dir, f"block_{i}.jpg")
            success = cv2.imwrite(fname, crop)
            if not success:
                print(f"[DEBUG] Failed to write block {i}, skipping")
                continue
            crops.append(fname)
            print(f"[DEBUG] Successfully saved block {i} to {fname}")
        return crops
    except Exception as e:
        raise ValueError(f"Error processing image {image_path}: {str(e)}")

def pair_by_order(q_crops, s_crops):
    n = min(len(q_crops), len(s_crops))
    return list(zip(q_crops[:n], s_crops[:n]))
