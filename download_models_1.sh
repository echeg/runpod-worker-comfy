#!/bin/bash

# Определяем базовую директорию для моделей
MODEL_DIR="/runpod-volume/models"

# Функция для скачивания файла, если его нет
download_if_not_exists() {
    local dir_path=$1
    local file_path=$2
    local url=$3

    # Создание директории, если ее нет
    mkdir -p "$dir_path"

    if [ -f "$file_path" ]; then
        echo "Файл уже существует: $file_path, пропускаем загрузку."
    else
        echo "Скачивание: $url -> $file_path"
        wget -O "$file_path" "$url"
    fi
}

# Пути к моделям
CLIP_INTERROGATOR_DIR="$MODEL_DIR/clip_interrogator/Salesforce/blip-image-captioning-base"
TEXT_GENERATOR_DIR="$MODEL_DIR/prompt_generator/text2image-prompt-generator"
ZH_EN_DIR="$MODEL_DIR/prompt_generator/opus-mt-zh-en"

CLIP_INTERROGATOR_MODEL="$CLIP_INTERROGATOR_DIR/pytorch_model.bin"
TEXT_GENERATOR_MODEL="$TEXT_GENERATOR_DIR/pytorch_model.bin"
ZH_EN_MODEL="$ZH_EN_DIR/pytorch_model.bin"

# URL моделей
CLIP_INTERROGATOR_URL="https://huggingface.co/Salesforce/blip-image-captioning-base/resolve/main/pytorch_model.bin"
TEXT_GENERATOR_URL="https://huggingface.co/succinctly/text2image-prompt-generator/resolve/main/pytorch_model.bin"
ZH_EN_URL="https://huggingface.co/Helsinki-NLP/opus-mt-zh-en/resolve/main/pytorch_model.bin"

# Скачивание моделей, если они отсутствуют
download_if_not_exists "$CLIP_INTERROGATOR_DIR" "$CLIP_INTERROGATOR_MODEL" "$CLIP_INTERROGATOR_URL"
download_if_not_exists "$TEXT_GENERATOR_DIR" "$TEXT_GENERATOR_MODEL" "$TEXT_GENERATOR_URL"
download_if_not_exists "$ZH_EN_DIR" "$ZH_EN_MODEL" "$ZH_EN_URL"

echo "Все модели скачаны или уже были установлены!"