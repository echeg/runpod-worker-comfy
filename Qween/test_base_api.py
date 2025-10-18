#!/usr/bin/env python3
"""
Быстрый тест базовой версии Qwen-ImageForFlo_2
"""

from gradio_client import Client
from PIL import Image
import time
import os

SERVER_URL = "http://127.0.0.1:7860"
OUTPUT_DIR = "/workspace/base_api_test"

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 80)
print("🧪 ТЕСТИРОВАНИЕ БАЗОВОЙ ВЕРСИИ")
print("=" * 80)

client = Client(SERVER_URL)
print("✅ Подключено к серверу")
print()

# ТЕСТ: Text2Image
print("📸 ТЕСТ: Text2Image")
print("-" * 80)

prompt = "SB_AI, character portrait, Ellie - Woman with shoulder-length wavy red-orange hair, green eyes, standing by mountain lake, detailed character model, cartoon art style"

start = time.time()
result = client.predict(
    prompt=prompt,
    negative_prompt="blurry, low quality, ugly",
    width=1024,
    height=1024,
    seed=100,
    randomize_seed=False,
    guidance_scale=2.5,
    num_inference_steps=30,
    api_name="/infer"
)

image_path, seed = result
elapsed = time.time() - start

output = os.path.join(OUTPUT_DIR, "text2img_test.png")
Image.open(image_path).save(output)

print(f"✅ УСПЕХ!")
print(f"   Время: {elapsed:.1f}s")
print(f"   Seed: {seed}")
print(f"   Сохранено: {output}")
print()
print("=" * 80)
print("🎉 ТЕСТ ЗАВЕРШЕН УСПЕШНО!")
print("=" * 80)

