#!/bin/bash

###############################################################################
# Quick Start Script - Минимальная установка и запуск
# Использует Hugging Face CLI для работы с приватными репозиториями
###############################################################################

set -e

echo "🚀 Quick Start - Qwen-Soloband Image Generator"
echo ""

# Проверка токена
if [ -z "$HF_TOKEN" ]; then
    if [ ! -z "$1" ]; then
        export HF_TOKEN="$1"
    else
        echo "❌ Ошибка: HF_TOKEN не указан"
        echo "Использование: HF_TOKEN=your_token $0"
        echo "Или: $0 your_token"
        exit 1
    fi
fi

# Определяем директорию (RunPod использует /workspace)
if [ -d "/workspace" ]; then
    WORK_DIR="/workspace"
    echo "📁 RunPod detected - using /workspace"
else
    WORK_DIR="."
fi

cd "$WORK_DIR"

# Устанавливаем HF CLI если нет
if ! command -v hf &> /dev/null; then
    echo "📦 Установка Hugging Face CLI..."
    pip install -q huggingface_hub[cli]
fi

# Отключаем hf_transfer для избежания ошибок
export HF_HUB_ENABLE_HF_TRANSFER=0

# Авторизуемся
echo "🔐 Авторизация в Hugging Face..."
hf auth login --token "$HF_TOKEN"

# Скачивание репозитория
if [ ! -d "Qwen-ImageForFlo_2" ]; then
    echo "📥 Скачивание репозитория через HF CLI..."
    hf download Gerchegg/Qwen-ImageForFlo_2 --repo-type space --local-dir Qwen-ImageForFlo_2
else
    echo "✅ Репозиторий уже существует"
fi

cd Qwen-ImageForFlo_2

# Установка зависимостей
echo "📦 Установка зависимостей..."
pip install -q -r requirements.txt

# Запуск
echo ""
echo "🎨 Запуск сервера..."
echo "⏳ Первый запуск займет 5-10 минут (загрузка модели ~40GB)"
echo ""

python app.py

