# 🌱 Automated Greenhouse Web App

This web application uses trained deep learning and computer vision models to detect plant diseases and nutrient deficiencies. It also monitors plant growth and visualizes real-time sensor data. Additionally, machine learning models predict optimal irrigation schedules, enabling efficient and data-driven farm management.

---

## 🔗 Model Training Code

This web application uses separately trained models. You can find the training code below:

- 🌿 Disease Detection (Faster R-CNN + FPN + EfficientNet-B4)  
  👉 [Disease Detection Training Code]()

- 🧪 Nutrient Deficiency Detection (EfficientNet-B0)  
  👉 [Nutrient Deficiency Training Code](YOUR_LINK_HERE)

- 📈 Growth Estimation (YOLO-based Detection)  
  👉 [Growth Estimation Training Code](YOUR_LINK_HERE)

- 💧 Irrigation Prediction (Random Forest Model)  
  👉 [Irrigation Prediction Training Code](YOUR_LINK_HERE)

---

## ⚠️ Model Weights

Due to size constraints, the following model files are not included in this repository:

- `classifier_model.pth`
- `detector_model.pth`

👉 These files are available here:  
[Google Drive Link]([YOUR_DRIVE_LINK](https://drive.google.com/drive/folders/1o69ZRhzx-y7Piha3jpoV7FIdCShSNY0y?usp=sharing))

Place them inside the `weights/` folder before running the project.

---

## ⚙️ Prerequisites

Make sure you have Python installed, then install required dependencies:

```bash
pip install -r requirements.txt
