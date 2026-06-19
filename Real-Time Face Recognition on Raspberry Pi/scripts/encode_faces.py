import os
import pickle
import face_recognition

DATASET_PATH = "../dataset"
ENCODINGS_PATH = "../data/encodings.pkl"

known_encodings = []
known_names = []

for person_name in os.listdir(DATASET_PATH):
    person_path = os.path.join(DATASET_PATH, person_name)

    if not os.path.isdir(person_path):
        continue

    for img_name in os.listdir(person_path):
        img_path = os.path.join(person_path, img_name)

        image = face_recognition.load_image_file(img_path)
        encodings = face_recognition.face_encodings(image)

        if len(encodings) > 0:
            known_encodings.append(encodings[0])
            known_names.append(person_name)

data = {"encodings": known_encodings, "names": known_names}

with open(ENCODINGS_PATH, "wb") as f:
    pickle.dump(data, f)

print("Encoding complete.")
