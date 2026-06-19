import cv2
import os

name = input("Enter name: ")
save_path = f"../dataset/{name}"

os.makedirs(save_path, exist_ok=True)

cap = cv2.VideoCapture(0)

count = 0

while count < 20:
    ret, frame = cap.read()
    if not ret:
        break

    cv2.imshow("Register Face", frame)

    key = cv2.waitKey(1)

    if key == ord('c'):
        img_path = os.path.join(save_path, f"{count}.jpg")
        cv2.imwrite(img_path, frame)
        print(f"Saved {img_path}")
        count += 1

    elif key == 27:
        break

cap.release()
cv2.destroyAllWindows()

print("Capture complete. Now run encode_faces.py")
