import cv2
import torch
import timm  # type: ignore
from torchvision import transforms
from PIL import Image
import os

from .model_detector import get_detector


device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

NUM_CLASSES = 8


class_names = [
    "Early Blight",
    "Black Spot",
    "Healthy",
    "Leaf Mold",
    "Bacterial Spot",
    "Target Spot",
    "Late Blight"
]

HEALTHY_CLASS_ID = 2


# ---------------- LOAD MODELS ----------------

detector = get_detector(NUM_CLASSES)

detector.load_state_dict(
    torch.load("weights/detector_model.pth", map_location=device)
)

detector.to(device)
detector.eval()


classifier = timm.create_model(
    "efficientnet_b4",
    num_classes=7
)

classifier.load_state_dict(
    torch.load("weights/classifier_model.pth", map_location=device)
)

classifier.to(device)
classifier.eval()


# ---------------- TRANSFORM ----------------

transform = transforms.Compose([
    transforms.Resize((380,380)),
    transforms.ToTensor()
])


# ---------------- MAIN FUNCTION ----------------

def detect_disease(img_path):

    img = cv2.imread(img_path)

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    tensor = torch.tensor(img_rgb)\
        .permute(2,0,1)\
        .float()/255

    tensor = tensor.unsqueeze(0).to(device)


    with torch.no_grad():
        outputs = detector(tensor)[0]


    boxes = outputs["boxes"]
    scores = outputs["scores"]

    results = []


    h, w, _ = img.shape


    # ---------------- DETECTIONS ----------------

    for box, score in zip(boxes, scores):

        if score < 0.2:
            continue

        x1, y1, x2, y2 = map(int, box.tolist())

        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(w, x2)
        y2 = min(h, y2)

        crop = img_rgb[y1:y2, x1:x2]

        if crop.size == 0:
            continue

        crop = Image.fromarray(crop)

        inp = transform(crop).unsqueeze(0).to(device)

        with torch.no_grad():

            pred = classifier(inp)

            cls = pred.argmax(1).item()


        results.append({

            "disease": class_names[cls],
            "confidence": float(score),
            "box": (x1,y1,x2,y2)

        })


    # ---------------- REMOVE HEALTHY IF DISEASE PRESENT ----------------

    has_disease = any(r["disease"] != "Healthy" for r in results)

    if has_disease:
        results = [r for r in results if r["disease"] != "Healthy"]


    # ---------------- DRAW BOUNDING BOXES ----------------

    for r in results:

        x1,y1,x2,y2 = r["box"]

        label = r["disease"]

        conf = r["confidence"]

        cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0),2)

        cv2.putText(
            img,
            f"{label} {conf:.2f}",
            (x1,y1-10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0,255,0),
            2
        )


    # ---------------- SAVE RESULT IMAGE ----------------

    os.makedirs("static/results", exist_ok=True)

    output_path = "static/results/disease_result.jpg"

    cv2.imwrite(output_path, img)


    # remove box coordinates before returning
    for r in results:
        del r["box"]


    return output_path, results