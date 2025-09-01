# app/forensics/ela.py
from PIL import Image, ImageChops, ImageEnhance
import numpy as np
import os

def save_ela(input_path: str, out_path: str, quality: int = 90):
    """
    Error Level Analysis (ELA) - quick visual tamper suspicion.
    """
    img = Image.open(input_path).convert("RGB")
    tmp_path = input_path + ".tmp.jpg"
    img.save(tmp_path, "JPEG", quality=quality)
    resaved = Image.open(tmp_path)
    ela = ImageChops.difference(img, resaved)
    extrema = ela.getextrema()
    max_diff = max([ex[1] for ex in extrema])
    scale = 255.0 / max(1, max_diff)
    ela = ImageEnhance.Brightness(ela).enhance(scale)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    ela.save(out_path)
    arr = np.array(ela).astype(np.float32) / 255.0
    suspicion = float(arr.mean())
    try:
        os.remove(tmp_path)
    except OSError:
        pass
    return out_path, suspicion
