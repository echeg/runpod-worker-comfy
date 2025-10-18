import gradio as gr
import numpy as np
import random
import json
import torch
from PIL import Image
import os
import time
import logging

# Опциональный импорт spaces для работы в Runpod
try:
    import spaces
    SPACES_AVAILABLE = True
except ImportError:
    SPACES_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("⚠️ spaces module not available - running without ZeroGPU support")

from diffusers import (
    DiffusionPipeline,
    QwenImageImg2ImgPipeline
)
from huggingface_hub import hf_hub_download

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

logger.info("=" * 60)
logger.info("LOADING QWEN-SOLOBAND ADVANCED")
logger.info("=" * 60)

hf_token = os.environ.get("HF_TOKEN")
device = "cuda" if torch.cuda.is_available() else "cpu"
dtype = torch.bfloat16

# Логируем GPU
logger.info(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    gpu_count = torch.cuda.device_count()
    logger.info(f"Number of GPUs: {gpu_count}")
    for i in range(gpu_count):
        logger.info(f"  GPU {i}: {torch.cuda.get_device_name(i)}")
        logger.info(f"    Memory: {torch.cuda.get_device_properties(i).total_memory / 1024**3:.1f} GB")

# =================================================================
# ЗАГРУЗКА МОДЕЛЕЙ
# =================================================================

# 1. Базовая модель для Text-to-Image
logger.info("\n[1/3] Loading base Text2Image model...")
model_id = os.environ.get("MODEL_ID", "Gerchegg/Qwen-Soloband-Diffusers")
model_revision = os.environ.get("MODEL_REVISION")

try:
    start_time = time.time()
    
    # Определяем device_map
    if gpu_count > 1:
        device_map = "balanced"
        logger.info(f"  Device map: balanced ({gpu_count} GPUs)")
    else:
        device_map = None
        logger.info("  Device map: single GPU")
    
    # Загружаем базовую модель
    load_kwargs = {
        "torch_dtype": dtype,
        "device_map": device_map,
        "token": hf_token,
        "local_files_only": True  # используем только локально предзагруженный кэш
    }
    if model_revision:
        load_kwargs["revision"] = model_revision

    pipe_txt2img = DiffusionPipeline.from_pretrained(model_id, **load_kwargs)
    
    if device_map is None:
        pipe_txt2img.to(device)
    
    load_time = time.time() - start_time
    logger.info(f"  ✓ Text2Image loaded in {load_time:.1f}s")
    
except Exception as e:
    logger.error(f"  ❌ Error loading Text2Image: {e}")
    raise

# 2. Image-to-Image модель (используем те же компоненты)
logger.info("\n[2/3] Creating Image2Image pipeline...")
try:
    # Создаем QwenImageImg2ImgPipeline переиспользуя компоненты Text2Image pipeline
    # Это правильный способ для Qwen-Image архитектуры
    pipe_img2img = QwenImageImg2ImgPipeline(
        vae=pipe_txt2img.vae,
        text_encoder=pipe_txt2img.text_encoder,
        tokenizer=pipe_txt2img.tokenizer,
        transformer=pipe_txt2img.transformer,
        scheduler=pipe_txt2img.scheduler
    )
    logger.info("  ✓ Image2Image pipeline created (reusing components)")
except Exception as e:
    logger.error(f"  ❌ Error creating Image2Image: {e}")
    pipe_img2img = None

# ControlNet не используется - убран для упрощения

# Оптимизации памяти
logger.info("\nApplying memory optimizations...")
for pipe in [pipe_txt2img, pipe_img2img]:
    if pipe and hasattr(pipe, 'vae'):
        if hasattr(pipe.vae, 'enable_tiling'):
            pipe.vae.enable_tiling()
        if hasattr(pipe.vae, 'enable_slicing'):
            pipe.vae.enable_slicing()

logger.info("  ✓ VAE tiling and slicing enabled")

logger.info("\n" + "=" * 60)
logger.info("✓ ALL MODELS LOADED")
logger.info("=" * 60)

# =================================================================
# HELPER FUNCTIONS
# =================================================================

def resize_image(input_image, max_size=1024):
    """Изменяет размер изображения с сохранением пропорций (кратно 8)"""
    w, h = input_image.size
    aspect_ratio = w / h
    
    if w > h:
        new_w = max_size
        new_h = int(new_w / aspect_ratio)
    else:
        new_h = max_size
        new_w = int(new_h * aspect_ratio)
    
    # Кратно 8
    new_w = new_w - (new_w % 8)
    new_h = new_h - (new_h % 8)
    
    if new_w == 0: new_w = 8
    if new_h == 0: new_h = 8
    
    return input_image.resize((new_w, new_h), Image.Resampling.LANCZOS)

# =================================================================
# LORA FUNCTIONS
# =================================================================

# Папка для локальных LoRA
LOCAL_LORA_DIR = "/workspace/loras"

# Базовые LoRA из HuggingFace Hub (загружаются по требованию)
HUB_LORAS = {
    "Realism": {
        "repo": "flymy-ai/qwen-image-realism-lora",
        "trigger": "Super Realism portrait of",
        "weights": "pytorch_lora_weights.safetensors",
        "source": "hub"
    },
    "Anime": {
        "repo": "alfredplpl/qwen-image-modern-anime-lora",
        "trigger": "Japanese modern anime style, ",
        "weights": "pytorch_lora_weights.safetensors",
        "source": "hub"
    }
    # Другие LoRA положите в /workspace/loras/ как .safetensors файлы
}

def scan_local_loras():
    """
    Сканирует папку /workspace/loras на наличие .safetensors файлов
    Возвращает dict с найденными LoRA
    """
    local_loras = {}
    
    if not os.path.exists(LOCAL_LORA_DIR):
        logger.info(f"  Local LoRA directory not found: {LOCAL_LORA_DIR}")
        return local_loras
    
    logger.info(f"  Scanning local LoRA directory: {LOCAL_LORA_DIR}")
    
    try:
        for file in os.listdir(LOCAL_LORA_DIR):
            if file.endswith('.safetensors'):
                lora_name = os.path.splitext(file)[0]  # Имя без расширения
                local_path = os.path.join(LOCAL_LORA_DIR, file)
                
                # Добавляем в список
                local_loras[lora_name] = {
                    "path": local_path,
                    "trigger": "",  # Без trigger word для локальных
                    "weights": file,
                    "source": "local"
                }
                
                logger.info(f"    ✓ Found local LoRA: {lora_name} ({file})")
    
    except Exception as e:
        logger.warning(f"  Error scanning local LoRA directory: {e}")
    
    return local_loras

# Сканируем локальные LoRA
logger.info("\nScanning for LoRA models...")
LOCAL_LORAS = scan_local_loras()

# Объединяем Hub и локальные LoRA
AVAILABLE_LORAS = {**HUB_LORAS, **LOCAL_LORAS}

if LOCAL_LORAS:
    logger.info(f"  ✓ Found {len(LOCAL_LORAS)} local LoRA(s)")
logger.info(f"  Total available LoRAs: {len(AVAILABLE_LORAS)}")

def load_lora_weights(pipeline, lora_name, lora_scale, hf_token):
    """
    Загружает LoRA веса в pipeline (ленивая загрузка)
    Hub LoRA скачиваются только при использовании
    Локальные LoRA загружаются из /workspace/loras/
    """
    if lora_name == "None" or lora_name not in AVAILABLE_LORAS:
        return None
    
    lora_info = AVAILABLE_LORAS[lora_name]
    
    try:
        if lora_info['source'] == 'hub':
            # Ленивая загрузка с HuggingFace Hub (скачивается при первом использовании)
            logger.info(f"  Loading LoRA from Hub: {lora_info['repo']}")
            logger.info(f"    (Downloading if not cached...)")
            
            pipeline.load_lora_weights(
                lora_info['repo'],
                weight_name=lora_info.get('weights', 'pytorch_lora_weights.safetensors'),
                token=hf_token
            )
            
            logger.info(f"    ✓ Hub LoRA loaded (cached for future use)")
        else:
            # Загрузка локального файла из /workspace/loras/
            logger.info(f"  Loading local LoRA: {lora_info['path']}")
            
            pipeline.load_lora_weights(
                lora_info['path'],
                adapter_name=lora_name
            )
            
            logger.info(f"    ✓ Local LoRA loaded")
        
        # Устанавливаем scale
        if hasattr(pipeline, 'set_adapters'):
            pipeline.set_adapters([lora_name], adapter_weights=[lora_scale])
        
        return lora_info.get('trigger', '')
        
    except Exception as e:
        logger.error(f"  ❌ Error loading LoRA {lora_name}: {e}")
        return None

# =================================================================
# GENERATION FUNCTIONS
# =================================================================

MAX_SEED = np.iinfo(np.int32).max

# Декоратор для spaces если доступен
def gpu_decorator(duration=180):
    def decorator(func):
        if SPACES_AVAILABLE:
            return spaces.GPU(duration=duration)(func)
        return func
    return decorator

@gpu_decorator(duration=180)
def generate_text2img(
    prompt,
    negative_prompt=" ",
    width=1664,
    height=928,
    seed=42,
    randomize_seed=False,
    guidance_scale=2.5,
    num_inference_steps=40,
    lora_name="None",
    lora_scale=1.0,
    progress=gr.Progress(track_tqdm=True)
):
    """Text-to-Image генерация"""
    
    logger.info("\n" + "=" * 60)
    logger.info("TEXT-TO-IMAGE GENERATION")
    logger.info("=" * 60)
    
    if randomize_seed:
        seed = random.randint(0, MAX_SEED)
    
    logger.info(f"  Prompt: {prompt[:100]}...")
    logger.info(f"  Size: {width}x{height}")
    logger.info(f"  Steps: {num_inference_steps}, CFG: {guidance_scale}")
    logger.info(f"  Seed: {seed}")
    logger.info(f"  LoRA: {lora_name} (scale: {lora_scale})")
    
    try:
        # Загружаем LoRA если выбрана
        trigger_word = None
        if lora_name != "None":
            trigger_word = load_lora_weights(pipe_txt2img, lora_name, lora_scale, hf_token)
            
            # Добавляем trigger word если есть
            if trigger_word:
                prompt = trigger_word + prompt
                logger.info(f"  Added trigger: {trigger_word}")
        
        generator = torch.Generator(device=device).manual_seed(seed)
        
        image = pipe_txt2img(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            num_inference_steps=num_inference_steps,
            true_cfg_scale=guidance_scale,
            generator=generator
        ).images[0]
        
        # Выгружаем LoRA после генерации
        if lora_name != "None":
            pipe_txt2img.unload_lora_weights()
        
        logger.info("  ✓ Generation completed")
        
        return image, seed
        
    except Exception as e:
        logger.error(f"  ❌ Error: {e}")
        raise

@gpu_decorator(duration=180)
def generate_img2img(
    input_image,
    prompt,
    negative_prompt=" ",
    strength=0.75,
    seed=42,
    randomize_seed=False,
    guidance_scale=2.5,
    num_inference_steps=40,
    lora_name="None",
    lora_scale=1.0,
    progress=gr.Progress(track_tqdm=True)
):
    """Image-to-Image генерация"""
    
    logger.info("\n" + "=" * 60)
    logger.info("IMAGE-TO-IMAGE GENERATION")
    logger.info("=" * 60)
    
    if input_image is None:
        raise gr.Error("Please upload an input image")
    
    if randomize_seed:
        seed = random.randint(0, MAX_SEED)
    
    # Изменяем размер изображения
    resized = resize_image(input_image, max_size=1024)
    
    logger.info(f"  Prompt: {prompt[:100]}...")
    logger.info(f"  Input size: {input_image.size} → {resized.size}")
    logger.info(f"  Strength: {strength}")
    logger.info(f"  Steps: {num_inference_steps}, CFG: {guidance_scale}")
    logger.info(f"  LoRA: {lora_name}")
    
    try:
        if pipe_img2img is None:
            raise gr.Error("Image2Image pipeline not available")
        
        # Загружаем LoRA если выбрана
        trigger_word = None
        if lora_name != "None":
            trigger_word = load_lora_weights(pipe_img2img, lora_name, lora_scale, hf_token)
            
            # Добавляем trigger word если есть
            if trigger_word:
                prompt = trigger_word + prompt
        
        generator = torch.Generator(device=device).manual_seed(seed)
        
        image = pipe_img2img(
            prompt=prompt,
            negative_prompt=negative_prompt,
            image=resized,
            strength=strength,
            num_inference_steps=num_inference_steps,
            true_cfg_scale=guidance_scale,
            generator=generator
        ).images[0]
        
        # Выгружаем LoRA
        if lora_name != "None":
            pipe_img2img.unload_lora_weights()
        
        logger.info("  ✓ Generation completed")
        
        return image, seed
        
    except Exception as e:
        logger.error(f"  ❌ Error: {e}")
        raise

# ControlNet функция убрана - не используется

# =================================================================
# GRADIO INTERFACE
# =================================================================

MAX_SEED = np.iinfo(np.int32).max

css = """
#col-container {
    margin: 0 auto;
    max-width: 1400px;
}
"""

with gr.Blocks(css=css, theme=gr.themes.Soft()) as demo:
    lora_choices = ["None"] + list(AVAILABLE_LORAS.keys())
    
    gr.Markdown(f"""
    # 🎨 Qwen Soloband - Image2Image + LoRA
    
    **Продвинутая модель генерации** с поддержкой Text-to-Image, Image-to-Image и LoRA стилей.
    
    ### ✨ Возможности:
    - 🖼️ **Text-to-Image** - Генерация из текста, разрешения до 2048×2048
    - 🔄 **Image-to-Image** - Модификация изображений с контролем strength (0.0-1.0)
    - 🎭 **LoRA Support** - {len(AVAILABLE_LORAS)} доступных стилей (Hub + локальные)
    - 🔌 **Full API** - Все функции доступны через API
    - ⚡ **Optimized** - VAE tiling/slicing, правильный QwenImageImg2ImgPipeline
    
    **Модель**: [Gerchegg/Qwen-Soloband-Diffusers](https://huggingface.co/Gerchegg/Qwen-Soloband-Diffusers)
    
    💡 **Local LoRAs**: Положите .safetensors файлы в `/workspace/loras/` - они появятся автоматически!
    """)
    
    with gr.Tabs() as tabs:
        
        # TAB 1: Text-to-Image
        with gr.Tab("📝 Text-to-Image"):
            with gr.Row():
                with gr.Column(scale=1):
                    t2i_prompt = gr.Text(
                        label="Prompt",
                        placeholder="SB_AI, a beautiful landscape...",
                        lines=3
                    )
                    
                    t2i_run = gr.Button("Generate", variant="primary")
                    
                    with gr.Accordion("Advanced Settings", open=False):
                        t2i_negative = gr.Text(label="Negative Prompt", value="blurry, low quality")
                        
                        with gr.Row():
                            t2i_width = gr.Slider(label="Width", minimum=512, maximum=2048, step=64, value=1664)
                            t2i_height = gr.Slider(label="Height", minimum=512, maximum=2048, step=64, value=928)
                        
                        with gr.Row():
                            t2i_steps = gr.Slider(label="Steps", minimum=1, maximum=50, step=1, value=40)
                            t2i_cfg = gr.Slider(label="CFG", minimum=0.0, maximum=7.5, step=0.1, value=2.5)
                        
                        with gr.Row():
                            t2i_seed = gr.Slider(label="Seed", minimum=0, maximum=MAX_SEED, step=1, value=0)
                            t2i_random_seed = gr.Checkbox(label="Random", value=True)
                        
                        t2i_lora = gr.Radio(
                            label="LoRA Style",
                            choices=lora_choices,
                            value="None",
                            info=f"Hub: {len(HUB_LORAS)}, Local: {len(LOCAL_LORAS)}"
                        )
                        t2i_lora_scale = gr.Slider(label="LoRA Strength", minimum=0.0, maximum=2.0, step=0.1, value=1.0)
                
                with gr.Column(scale=1):
                    t2i_output = gr.Image(label="Generated Image")
                    t2i_seed_output = gr.Number(label="Used Seed")
        
        # TAB 2: Image-to-Image
        with gr.Tab("🔄 Image-to-Image"):
            with gr.Row():
                with gr.Column(scale=1):
                    i2i_input = gr.Image(type="pil", label="Input Image")
                    i2i_prompt = gr.Text(
                        label="Prompt",
                        placeholder="Transform this image into...",
                        lines=3
                    )
                    
                    i2i_strength = gr.Slider(
                        label="Denoising Strength",
                        info="0.0 = original image, 1.0 = complete redraw",
                        minimum=0.0,
                        maximum=1.0,
                        step=0.05,
                        value=0.75
                    )
                    
                    i2i_run = gr.Button("Generate", variant="primary")
                    
                    with gr.Accordion("Advanced Settings", open=False):
                        i2i_negative = gr.Text(label="Negative Prompt", value="blurry, low quality")
                        
                        with gr.Row():
                            i2i_steps = gr.Slider(label="Steps", minimum=1, maximum=50, step=1, value=40)
                            i2i_cfg = gr.Slider(label="CFG", minimum=0.0, maximum=7.5, step=0.1, value=2.5)
                        
                        with gr.Row():
                            i2i_seed = gr.Slider(label="Seed", minimum=0, maximum=MAX_SEED, step=1, value=0)
                            i2i_random_seed = gr.Checkbox(label="Random", value=True)
                        
                        i2i_lora = gr.Radio(
                            label="LoRA Style",
                            choices=lora_choices,
                            value="None",
                            info=f"Hub: {len(HUB_LORAS)}, Local: {len(LOCAL_LORAS)}"
                        )
                        i2i_lora_scale = gr.Slider(label="LoRA Strength", minimum=0.0, maximum=2.0, step=0.1, value=1.0)
                
                with gr.Column(scale=1):
                    i2i_output = gr.Image(label="Generated Image")
                    i2i_seed_output = gr.Number(label="Used Seed")
        
    
    # Event handlers
    t2i_run.click(
        fn=generate_text2img,
        inputs=[
            t2i_prompt, t2i_negative, t2i_width, t2i_height,
            t2i_seed, t2i_random_seed, t2i_cfg, t2i_steps,
            t2i_lora, t2i_lora_scale
        ],
        outputs=[t2i_output, t2i_seed_output],
        api_name="text2img"
    )
    
    i2i_run.click(
        fn=generate_img2img,
        inputs=[
            i2i_input, i2i_prompt, i2i_negative, i2i_strength,
            i2i_seed, i2i_random_seed, i2i_cfg, i2i_steps,
            i2i_lora, i2i_lora_scale
        ],
        outputs=[i2i_output, i2i_seed_output],
        api_name="img2img"
    )

if __name__ == "__main__":
    demo.launch(
        show_api=True,
        share=False
    )

