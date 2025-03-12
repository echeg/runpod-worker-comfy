#!/bin/bash

# Определяем базовую директорию для моделей
MODEL_DIR="/runpod-volume/models"

# Функция для скачивания файла, если его нет
download_if_not_exists() {
    local dir_path=$1
    local filename=$2
    local url=$3
    local file_path="$dir_path/$filename"

    # Создание директории, если ее нет
    mkdir -p "$dir_path"

    if [ -f "$file_path" ]; then
        echo "Файл уже существует: $file_path, пропускаем загрузку."
    else
        echo "Скачивание: $url -> $file_path"
        wget -O "$file_path" "$url"
    fi
}

# Скачивание моделей, если они отсутствуют
download_if_not_exists "$MODEL_DIR/clip_interrogator/Salesforce/blip-image-captioning-base" "pytorch_model.bin" "https://huggingface.co/Salesforce/blip-image-captioning-base/resolve/main/pytorch_model.bin"
download_if_not_exists "$MODEL_DIR/prompt_generator/text2image-prompt-generator" "pytorch_model.bin" "https://huggingface.co/succinctly/text2image-prompt-generator/resolve/main/pytorch_model.bin"
download_if_not_exists "$MODEL_DIR/prompt_generator/opus-mt-zh-en" "pytorch_model.bin" "https://huggingface.co/Helsinki-NLP/opus-mt-zh-en/resolve/main/pytorch_model.bin"
download_if_not_exists "$MODEL_DIR/checkpoints" "v1-5-pruned-emaonly-fp16.safetensors" "https://huggingface.co/Comfy-Org/stable-diffusion-v1-5-archive/resolve/main/v1-5-pruned-emaonly-fp16.safetensors?download=true"

echo "Все модели скачаны или уже были установлены!"