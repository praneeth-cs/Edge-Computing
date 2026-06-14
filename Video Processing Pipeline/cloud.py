from flask import Flask, request
import os

app = Flask(__name__)

BASE_FOLDER = "received_frames"
os.makedirs(BASE_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_frame():
    run_id = request.form['run_id']
    frame_type = request.form.get('frame_type', 'unknown')
    file = request.files['frame']

    run_folder = os.path.join(BASE_FOLDER, run_id)
    os.makedirs(run_folder, exist_ok=True)

    file.save(os.path.join(run_folder, file.filename))

    print(f"Received {file.filename} | Type: {frame_type}")

    return "Frame received", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)