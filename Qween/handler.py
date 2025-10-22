import os
import io
import base64
from typing import Dict, Any

from PIL import Image

import runpod
from runpod.serverless.utils import rp_upload

# Импортируем функции генерации из приложения.
# Внутри app.py запуск UI защищен блоком `if __name__ == "__main__"`,
# поэтому при импорте UI не стартует, а модели и функции уже доступны.
from app import generate_text2img, generate_img2img  # type: ignore


REFRESH_WORKER = os.environ.get("REFRESH_WORKER", "false").lower() == "true"
USE_S3 = bool(os.environ.get("BUCKET_ENDPOINT_URL"))


def pil_to_base64(image: Image.Image, format: str = "PNG") -> str:
    buffer = io.BytesIO()
    image.save(buffer, format=format)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def handler(job: Dict[str, Any]) -> Dict[str, Any]:
    """
    Обработчик Runpod Serverless.

    Ожидаемый формат входа в job["input"]:
    {
      "mode": "text2img" | "img2img",
      "prompt": "string",
      "negative_prompt": "string",

      // text2img
      "width": 1664,
      "height": 928,

      // img2img
      "input_image": "<BASE64 PNG/JPEG>",
      "strength": 0.75,

      // общие
      "steps": 40,
      "cfg": 2.5,
      "seed": 42,
      "randomize_seed": false,
      "lora_name": "None",
      "lora_scale": 1.0
    }
    """
    try:
        data = job.get("input") or {}
        mode = (data.get("mode") or "text2img").lower()
        prompt = data.get("prompt", "")
        negative_prompt = data.get("negative_prompt", " ")

        # Общие параметры
        steps = int(data.get("steps", 40))
        cfg = float(data.get("cfg", 2.5))
        seed = int(data.get("seed", 42))
        randomize_seed = bool(data.get("randomize_seed", False))
        lora_name = data.get("lora_name", "None")
        lora_scale = float(data.get("lora_scale", 1.0))

        if mode == "text2img":
            width = int(data.get("width", 1664))
            height = int(data.get("height", 928))

            image, used_seed = generate_text2img(
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                seed=seed,
                randomize_seed=randomize_seed,
                guidance_scale=cfg,
                num_inference_steps=steps,
                lora_name=lora_name,
                lora_scale=lora_scale,
            )

        elif mode == "img2img":
            b64 = data.get("input_image")
            if not b64:
                return {"error": "input_image (base64) is required for img2img"}

            try:
                raw = base64.b64decode(b64)
                input_image = Image.open(io.BytesIO(raw)).convert("RGB")
            except Exception as e:  # noqa: BLE001
                return {"error": f"Invalid base64 input_image: {e}"}

            strength = float(data.get("strength", 0.75))

            image, used_seed = generate_img2img(
                input_image=input_image,
                prompt=prompt,
                negative_prompt=negative_prompt,
                strength=strength,
                seed=seed,
                randomize_seed=randomize_seed,
                guidance_scale=cfg,
                num_inference_steps=steps,
                lora_name=lora_name,
                lora_scale=lora_scale,
            )

        else:
            return {"error": f"Unknown mode: {mode}"}

        # Отдача результата: S3 (если настроено) или base64
        if USE_S3:
            out_path = f"/tmp/{job['id']}.png"
            image.save(out_path, "PNG")
            url = rp_upload.upload_image(job["id"], out_path)
            result = {
                "status": "success",
                "mode": mode,
                "image": url,
                "seed": used_seed,
            }
        else:
            b64_out = pil_to_base64(image, format="PNG")
            result = {
                "status": "success",
                "mode": mode,
                "image": b64_out,
                "seed": used_seed,
            }

        result["refresh_worker"] = REFRESH_WORKER
        return result

    except Exception as e:  # noqa: BLE001
        return {"error": f"Unhandled error: {e}"}


if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})



