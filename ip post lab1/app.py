
from flask import Flask, render_template, request, jsonify, send_file
import cv2
import numpy as np
import os
import uuid

app = Flask(__name__)
UPLOADS = "uploads"
OUTPUTS = "outputs"
os.makedirs(UPLOADS, exist_ok=True)
os.makedirs(OUTPUTS, exist_ok=True)

def load_image(path):
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Invalid image.")
    return img

def save_result(img, ext=".png"):
    name = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(OUTPUTS, name)
    cv2.imwrite(path, img)
    return name

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/process", methods=["POST"])
def process():
    try:
        practical = request.form.get("practical")
        operation = request.form.get("operation", "")
        file = request.files.get("image")

        if not file:
            return jsonify(error="Please upload an image."), 400

        original_name = f"{uuid.uuid4().hex}_{file.filename}"
        input_path = os.path.join(UPLOADS, original_name)
        file.save(input_path)
        img = load_image(input_path)

        if practical == "3":
            if operation == "grayscale":
                result = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            elif operation == "resize":
                w = int(request.form.get("width", 250))
                h = int(request.form.get("height", 200))
                if w <= 0 or h <= 0:
                    raise ValueError("Width and height must be positive.")
                result = cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA)
            elif operation == "crop":
                x = int(request.form.get("x", 100))
                y = int(request.form.get("y", 100))
                w = int(request.form.get("width", 200))
                h = int(request.form.get("height", 200))
                if x < 0 or y < 0 or w <= 0 or h <= 0 or x+w > img.shape[1] or y+h > img.shape[0]:
                    raise ValueError("Crop area is outside the image.")
                result = img[y:y+h, x:x+w]
            else:
                result = img

        elif practical == "4":
            result = 255 - img

        elif practical == "5":
            brightness = float(request.form.get("brightness", 10))
            contrast = float(request.form.get("contrast", 1.5))
            result = cv2.convertScaleAbs(img, alpha=contrast, beta=brightness)

        elif practical == "6":
            if operation == "laplacian":
                lap = cv2.Laplacian(img, cv2.CV_64F)
                result = cv2.convertScaleAbs(lap)
            else:
                kernel = np.array([[0,-1,0],[-1,5,-1],[0,-1,0]])
                result = cv2.filter2D(img, -1, kernel)

        elif practical == "7":
            if operation == "averaging":
                result = cv2.blur(img, (5,5))
            elif operation == "gaussian":
                result = cv2.GaussianBlur(img, (5,5), 0)
            elif operation == "median":
                result = cv2.medianBlur(img, 5)
            else:
                result = cv2.bilateralFilter(img, 9, 75, 75)

        elif practical == "8":
            mask_file = request.files.get("mask")
            if not mask_file:
                return jsonify(error="Practical 8 requires a mask image. Use the mask drawing interface in the prototype."), 400
            mask_name = f"{uuid.uuid4().hex}_mask.png"
            mask_path = os.path.join(UPLOADS, mask_name)
            mask_file.save(mask_path)
            mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
            if mask is None:
                raise ValueError("Invalid mask.")
            mask = cv2.resize(mask, (img.shape[1], img.shape[0]))
            method = cv2.INPAINT_TELEA if operation == "telea" else cv2.INPAINT_NS
            result = cv2.inpaint(img, mask, 3, method)

        elif practical == "9":
            quality = int(request.form.get("quality", 30))
            compression = int(request.form.get("compression", 9))
            if operation == "lossless":
                name = f"{uuid.uuid4().hex}.png"
                path = os.path.join(OUTPUTS, name)
                cv2.imwrite(path, img, [cv2.IMWRITE_PNG_COMPRESSION, compression])
            else:
                name = f"{uuid.uuid4().hex}.jpg"
                path = os.path.join(OUTPUTS, name)
                cv2.imwrite(path, img, [cv2.IMWRITE_JPEG_QUALITY, quality])
            original_size = os.path.getsize(input_path)
            output_size = os.path.getsize(path)
            return jsonify(
                result=f"/outputs/{name}",
                download=f"/download/{name}",
                original_kb=round(original_size/1024, 2),
                compressed_kb=round(output_size/1024, 2),
                ratio=round(original_size/output_size, 2) if output_size else 0
            )

        else:
            raise ValueError("Unknown practical.")

        name = save_result(result)
        return jsonify(result=f"/outputs/{name}", download=f"/download/{name}")

    except Exception as e:
        return jsonify(error=str(e)), 400

@app.route("/outputs/<name>")
def outputs(name):
    return send_file(os.path.join(OUTPUTS, name))

@app.route("/download/<name>")
def download(name):
    return send_file(os.path.join(OUTPUTS, name), as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
