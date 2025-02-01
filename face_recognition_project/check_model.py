import os
import face_recognition_models

model_path = os.path.join(
    os.path.dirname(face_recognition_models.__file__),
    'models',
    'shape_predictor_68_face_landmarks.dat'
)

print(f"Model yolu: {model_path}")
print(f"Model mevcut: {os.path.exists(model_path)}")