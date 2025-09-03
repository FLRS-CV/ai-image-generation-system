from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import websocket
import uuid
import json
import os, io
from PIL import Image
import base64
import copy

app = Flask(__name__)
CORS(app, origins=["*"])

COMFY_HOST = "127.0.0.1"
COMFY_PORT = 8188
CLIENT_ID = str(uuid.uuid4())
SERVER_ADDRESS = f"{COMFY_HOST}:{COMFY_PORT}"

def queue_prompt(prompt, prompt_id):
    import urllib.request
    data = json.dumps({"prompt": prompt, "client_id": CLIENT_ID, "prompt_id": prompt_id}).encode("utf-8")
    req = urllib.request.Request(f"http://{SERVER_ADDRESS}/prompt", data=data)
    urllib.request.urlopen(req).read()

def get_image(filename, subfolder, folder_type):
    import urllib.parse, urllib.request
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen(f"http://{SERVER_ADDRESS}/view?{url_values}") as response:
        return response.read()

def get_history(prompt_id):
    import urllib.request
    with urllib.request.urlopen(f"http://{SERVER_ADDRESS}/history/{prompt_id}") as response:
        return json.loads(response.read())

def generate_images_ws(ws, prompt, seed=None):
    prompt_id = str(uuid.uuid4())
    if seed is not None and "107" in prompt:
        prompt["107"]["inputs"]["value"] = seed
    queue_prompt(prompt, prompt_id)
    output_images = {}

    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message["type"] == "executing":
                data = message["data"]
                if data["node"] is None and data["prompt_id"] == prompt_id:
                    break
        else:
            continue

    history = get_history(prompt_id)[prompt_id]
    for node_id, node_output in history["outputs"].items():
        if "images" in node_output and node_output["images"]:
            images_data = [get_image(img["filename"], img["subfolder"], img["type"]) for img in node_output["images"]]
            output_images[node_id] = images_data

    return output_images

@app.route("/generate", methods=["POST"])
def generate():
    print(f"Received generate request")
    if "image_file" not in request.files or "prompt_text" not in request.form:
        print("Missing image or prompt")
        return jsonify({"error": "Missing image or prompt"}), 400

    image_file = request.files["image_file"]
    prompt_text = request.form.get("prompt_text", "")
    negative_prompt_text = request.form.get("negative_prompt_text", "")
    ckpt_name = request.form.get("ckpt_name", "juggernaut_reborn.safetensors")
    seed_str = request.form.get("seed", "")
    workflow_file = request.form.get("workflow", "joger.json")
    num_images = int(request.form.get("num_images", 1))

    print(f"Parameters: prompt='{prompt_text}', workflow='{workflow_file}', num_images={num_images}")

    os.makedirs("temp_uploads", exist_ok=True)
    input_path = os.path.abspath(os.path.join("temp_uploads", image_file.filename or "input.png"))
    image_file.save(input_path)
    print(f"Saved input image to: {input_path}")

    # Ensure workflow file path is absolute
    if not os.path.isabs(workflow_file):
        workflow_file = os.path.abspath(workflow_file)
    
    print(f"Loading workflow from: {workflow_file}")

    try:
        with open(workflow_file, "r", encoding="utf-8") as f:
            base_prompt = json.load(f)
        print("Workflow loaded successfully")
    except Exception as e:
        print(f"Failed to load workflow: {e}")
        return jsonify({"error": f"Failed to load workflow {workflow_file}: {e}"}), 400

    results = []

    try:
        # Open WebSocket once for all iterations
        print(f"Connecting to ComfyUI at ws://{SERVER_ADDRESS}/ws?clientId={CLIENT_ID}")
        ws = websocket.WebSocket()
        ws.connect(f"ws://{SERVER_ADDRESS}/ws?clientId={CLIENT_ID}")
        print("WebSocket connected successfully")
    except Exception as e:
        print(f"Failed to connect to ComfyUI: {e}")
        return jsonify({"error": f"Failed to connect to ComfyUI: {e}"}), 500

    for i in range(num_images):
        print(f"Generating image {i+1}/{num_images}")
        prompt = copy.deepcopy(base_prompt)
        if "9" in prompt:
            prompt["9"]["inputs"]["image"] = input_path
        if "32" in prompt:
            prompt["32"]["inputs"]["value"] = prompt_text
        if "33" in prompt and negative_prompt_text:
            prompt["33"]["inputs"]["value"] = negative_prompt_text
        if "3" in prompt:
            prompt["3"]["inputs"]["ckpt_name"] = ckpt_name
        if "38" in prompt:
            prompt["38"]["inputs"]["ckpt_name"] = ckpt_name

        seed_val = int(seed_str) + i if seed_str.isdigit() else None
        print(f"Using seed: {seed_val}")
        
        try:
            images = generate_images_ws(ws, prompt, seed=seed_val)
            print(f"Generated images for iteration {i+1}: {list(images.keys())}")
        except Exception as e:
            print(f"Error generating images: {e}")
            ws.close()
            return jsonify({"error": f"Failed to generate images: {e}"}), 500

        if "159" in images and images["159"]:
            image_data = images["159"][0]
            image = Image.open(io.BytesIO(image_data))

            os.makedirs("generated", exist_ok=True)
            filename = f"generated_{uuid.uuid4().hex}.png"
            save_path = os.path.join("generated", filename)
            image.save(save_path, format="PNG")
            file_url = request.host_url.rstrip("/") + f"/generated/{filename}"

            buf = io.BytesIO()
            image.save(buf, format="PNG")
            img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

            results.append({
                "image": f"data:image/png;base64,{img_b64}",
                "file_url": file_url,
                "seed": seed_val
            })
            print(f"Successfully generated image {i+1}")
        else:
            print(f"No image data found in node 159 for iteration {i+1}")

    ws.close()
    print(f"Generated {len(results)} images total")

    if results:
        return jsonify({"results": results})
    else:
        return jsonify({"error": "No images generated"}), 500

@app.route("/generated/<path:filename>")
def get_generated(filename):
    directory = os.path.abspath("generated")
    return send_from_directory(directory, filename, as_attachment=False)

if __name__ == "__main__":
    os.makedirs("outputs", exist_ok=True)
    os.makedirs("generated", exist_ok=True)
    app.run(host="0.0.0.0", port=5000, debug=True)
