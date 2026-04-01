import cv2
import numpy as np
from skimage.morphology import skeletonize  # type: ignore
from ultralytics import YOLO # type: ignore
import torch

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


# ---------------- VEGETATION MODEL ----------------

class VegetationGrowthModel:

    def segment(self, image):

        img = image.astype(np.float32) / 255.0
        B, G, R = cv2.split(img)

        exg = 2 * G - R - B
        exg = (exg - exg.min()) / (exg.max() - exg.min() + 1e-6)
        exg_mask = (exg > 0.2).astype(np.uint8) * 255

        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        lower = np.array([35, 40, 40])
        upper = np.array([85, 255, 255])

        hsv_mask = cv2.inRange(hsv, lower, upper)

        mask = cv2.bitwise_and(exg_mask, hsv_mask)

        kernel = np.ones((7,7), np.uint8)

        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask)

        clean_mask = np.zeros_like(mask)

        for i in range(1, num_labels):
            area = stats[i, cv2.CC_STAT_AREA]
            if area > 500:
                clean_mask[labels == i] = 255

        return clean_mask


    def extract_features(self, mask):

        leaf_area = np.sum(mask > 0)
        area_ratio = leaf_area / mask.size

        contours,_ = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        leaf_count = sum(1 for c in contours if cv2.contourArea(c) > 300)

        binary = (mask > 0).astype(np.uint8)

        kernel = np.ones((7,7), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

        skeleton = skeletonize(binary).astype(np.uint8)

        endpoints = []

        for y in range(1, skeleton.shape[0]-1):
            for x in range(1, skeleton.shape[1]-1):

                if skeleton[y,x]:

                    neighbors = np.sum(
                        skeleton[y-1:y+2, x-1:x+2]
                    ) - 1

                    if neighbors == 1:
                        endpoints.append((x,y))

        branch_complexity = len(endpoints)

        return area_ratio, leaf_count, branch_complexity, skeleton, endpoints


    def compute_growth(self, area_ratio, leaf_count, branch_complexity):

        count_score = min(leaf_count / 40, 1.0)
        branch_score = min(branch_complexity / 120, 1.0)

        vegetation_index = (
            0.45 * area_ratio +
            0.30 * count_score +
            0.25 * branch_score
        )

        growth_percent = vegetation_index * 58

        return min(58, max(0, growth_percent))


# ---------------- HYBRID SYSTEM ----------------

class HybridGrowthSystem:

    def __init__(self, yolo_path=None):

        self.vegetation_model = VegetationGrowthModel()

        if yolo_path:
            self.detector = YOLO(yolo_path)
        else:
            self.detector = None


    def detect_fruit(self, image):

        if self.detector is None:
            return False, None

        results = self.detector(image, verbose=False)[0]

        if len(results.boxes) == 0:
            return False, None

        return True, results


    def predict(self, image):

        fruit_present, results = self.detect_fruit(image)

        mask = self.vegetation_model.segment(image)

        area_ratio, leaf_count, branch_complexity, skeleton, endpoints = \
            self.vegetation_model.extract_features(mask)

        veg_growth = self.vegetation_model.compute_growth(
            area_ratio,
            leaf_count,
            branch_complexity
        )

        if not fruit_present:

            return {
                "mode":"vegetative",
                "growth":veg_growth,
                "mask":mask,
                "skeleton":skeleton,
                "endpoints":endpoints,
                "detections":None
            }

        else:

            full_growth = 58 + (veg_growth / 58) * 42

            return {
                "mode":"fruiting",
                "growth":min(100, full_growth),
                "mask":None,
                "skeleton":None,
                "endpoints":None,
                "detections":results
            }


# ---------------- VISUALIZATION ----------------

def visualize_vegetation(image, mask, skeleton, endpoints, growth):

    kernel = np.ones((9,9), np.uint8)
    thick = cv2.dilate(skeleton, kernel, iterations=1)

    overlay = image.copy()

    overlay[thick > 0] = [255,0,0]

    for (x,y) in endpoints:
        cv2.circle(overlay,(x,y),10,(0,0,255),-1)

    cv2.putText(
        overlay,
        f"Growth: {growth:.2f}%",
        (30,50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0,255,0),
        2
    )

    return overlay


def visualize_yolo(image, results, growth):

    annotated = results.plot()

    cv2.putText(
        annotated,
        f"Growth: {growth:.2f}%",
        (30,50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0,255,0),
        2
    )

    return annotated