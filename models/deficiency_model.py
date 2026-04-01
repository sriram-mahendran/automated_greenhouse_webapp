from PIL import Image
import torch
from torchvision import transforms, models
import torch.nn as nn


classes = [
    'healthy',
    'magnesium',
    'nitrogen',
    'potassium'
]


transform = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor()
])


model = models.efficientnet_b0(weights=None)

model.classifier[1] = nn.Linear(
    model.classifier[1].in_features,
    4
)


model.load_state_dict(
    torch.load("weights/tomato_deficiency_model.pth",
               weights_only=True)
)

model.eval()


def predict_deficiency(img_path):

    img = Image.open(img_path).convert("RGB")

    img = transform(img).unsqueeze(0)

    with torch.no_grad():

        outputs = model(img)

        _, predicted = torch.max(outputs,1)

    return classes[predicted.item()]