"""
ComfyUI Wrapper Service
Handles all ComfyUI communication and image generation logic
"""
import websocket
import uuid
import json
import os, io
from PIL import Image
import base64
import copy
import random

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

def empty_2_furnished(input_path, num_images, style="scandinavian"):
    """
    Generate furnished room images from empty room input
    
    Args:
        input_path (str): Path to input image file
        num_images (int): Number of images to generate
        style (str): Style of furnishing (default: scandinavian)
    
    Returns:
        dict: Response with status and results
    """
    workflow_file = os.path.join(os.path.dirname(__file__), "..", "..", "joger.json")
    prompt_text = "A modern minimal living room, clean design, photorealistic"
    negative_prompt_text = "lowres, blurry, distorted, cartoonish"
    ckpt_name = "juggernaut_reborn.safetensors"
    
    # Style-specific prompts
    if style == "scandinavian":
        prompt_text = "Scandinavian living room, modern, minimalistic, bright, cozy, clean lines, natural materials, wood, white walls, large windows, plants, soft lighting"
    
    # Load workflow
    try:
        with open(workflow_file, "r", encoding="utf-8") as f:
            base_prompt = json.load(f)
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to load workflow {workflow_file}: {e}",
            "results": []
        }

    results = []

    try:
        # Open WebSocket connection to ComfyUI
        ws = websocket.WebSocket()
        ws.connect(f"ws://{SERVER_ADDRESS}/ws?clientId={CLIENT_ID}")
        
        # Generate multiple images
        for i in range(num_images):
            prompt = copy.deepcopy(base_prompt)
            
            # Configure prompt parameters
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

            # Generate random seed for variation
            seed_val = random.randint(1000000, 9999999)
            
            # Generate image
            images = generate_images_ws(ws, prompt, seed=seed_val)

            if "159" in images and images["159"]:
                image_data = images["159"][0]
                image = Image.open(io.BytesIO(image_data))

                # Save generated image
                os.makedirs("generated", exist_ok=True)
                filename = f"generated_{uuid.uuid4().hex}.png"
                save_path = os.path.join("generated", filename)
                image.save(save_path, format="PNG")

                # Convert to base64 for response
                buf = io.BytesIO()
                image.save(buf, format="PNG")
                img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

                results.append({
                    "image": f"data:image/png;base64,{img_b64}",
                    "style": style,
                    "seed": seed_val,
                    "file_path": save_path,
                    "filename": filename,
                    "index": i + 1
                })

        ws.close()
        
        return {
            "status": "success",
            "message": f"Successfully generated {len(results)} images",
            "results": results
        }
        
    except Exception as e:
        return {
            "status": "error", 
            "message": f"Error during image generation: {str(e)}",
            "results": []
        }
