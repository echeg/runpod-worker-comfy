# FLO AI Vector Docker Images

Этот репозиторий содержит Docker образы для моделей FLO AI Vector Characters и Objects для ComfyUI, основанных на базовом образе flux1-dev-nodes.

## Доступные образы

### 1. FLO AI Vector Characters
- **Docker образ**: `echeg/flux1-dev-flo-chars:0.4.3`
- **Dockerfile**: `DockerfileFLOVectorCharacters`
- **Модель**: `FLO_AI_VectorCharacters_NL_Slow_v2.safetensors`

### 2. FLO AI Vector Objects
- **Docker образ**: `echeg/flux1-dev-flo-objs:0.4.3`
- **Dockerfile**: `DockerfileFLOVectorObj`
- **Модель**: `FLO_AI_VectorObjects_NL_Slow_v2.safetensors`

## Требования

- Docker установлен на вашей системе
- Файлы моделей должны находиться в каталоге `models/Models/`:
  - `FLO_AI_VectorCharacters_NL_Slow_v2.safetensors`
  - `FLO_AI_VectorObjects_NL_Slow_v2.safetensors`

## Структура каталогов

```
runpod-worker-comfy/
├── DockerfileFLOVectorCharacters
├── DockerfileFLOVectorObj
└── models/
    └── Models/
        ├── FLO_AI_VectorCharacters_NL_Slow_v2.safetensors
        └── FLO_AI_VectorObjects_NL_Slow_v2.safetensors
```

## Сборка образов

### FLO AI Vector Characters
```bash
# Перейдите в корневую папку проекта
cd runpod-worker-comfy

# Соберите Docker образ для персонажей (Linux платформа)
docker build --platform=linux/amd64 -f DockerfileFLOVectorCharacters -t echeg/flux1-dev-flo-chars:0.4.3 .
```

### FLO AI Vector Objects
```bash
# Соберите Docker образ для объектов (Linux платформа)
docker build --platform=linux/amd64 -f DockerfileFLOVectorObj -t echeg/flux1-dev-flo-objs:0.4.3 .
```

### Сборка обоих образов одновременно
```bash
# Соберите оба образа для Linux платформы
docker build --platform=linux/amd64 -f DockerfileFLOVectorCharacters -t echeg/flux1-dev-flo-chars:0.4.3 . && \
docker build --platform=linux/amd64 -f DockerfileFLOVectorObj -t echeg/flux1-dev-flo-objs:0.4.3 .
```

### Сборка для нативной платформы (если нужно)
```bash
# Для локального тестирования можно собрать без указания платформы
docker build -f DockerfileFLOVectorCharacters -t echeg/flux1-dev-flo-chars:0.4.3-local .
docker build -f DockerfileFLOVectorObj -t echeg/flux1-dev-flo-objs:0.4.3-local .
```

## Запуск контейнеров

### FLO AI Vector Characters
```bash
# Базовый запуск
docker run -p 8188:8188 echeg/flux1-dev-flo-chars:0.4.3

# Запуск с volume для вывода
docker run -p 8188:8188 -v $(pwd)/output:/comfyui/output echeg/flux1-dev-flo-chars:0.4.3

# Запуск в фоновом режиме
docker run -d -p 8188:8188 --name flo-chars echeg/flux1-dev-flo-chars:0.4.3
```

### FLO AI Vector Objects
```bash
# Базовый запуск
docker run -p 8189:8188 echeg/flux1-dev-flo-objs:0.4.3

# Запуск с volume для вывода
docker run -p 8189:8188 -v $(pwd)/output:/comfyui/output echeg/flux1-dev-flo-objs:0.4.3

# Запуск в фоновом режиме
docker run -d -p 8189:8188 --name flo-objs echeg/flux1-dev-flo-objs:0.4.3
```

## Доступ к интерфейсу

После запуска контейнеров ComfyUI будет доступен по адресам:
- **Characters**: http://localhost:8188
- **Objects**: http://localhost:8189

## Расположение моделей в контейнерах

### FLO AI Vector Characters
- **Основной каталог**: `/comfyui/models/diffusion_models/FLO_AI_VectorCharacters_NL_Slow_v2.safetensors`
- **Каталог checkpoints**: `/comfyui/models/checkpoints/FLO_AI_VectorCharacters_NL_Slow_v2.safetensors` (симлинк)
- **Каталог unet**: `/comfyui/models/unet/FLO_AI_VectorCharacters_NL_Slow_v2.safetensors` (симлинк)

### FLO AI Vector Objects
- **Основной каталог**: `/comfyui/models/diffusion_models/FLO_AI_VectorObjects_NL_Slow_v2.safetensors`
- **Каталог checkpoints**: `/comfyui/models/checkpoints/FLO_AI_VectorObjects_NL_Slow_v2.safetensors` (симлинк)
- **Каталог unet**: `/comfyui/models/unet/FLO_AI_VectorObjects_NL_Slow_v2.safetensors` (симлинк)

## Публикация в Docker Hub

```bash
# Войдите в Docker Hub
docker login

# Опубликуйте образы
docker push echeg/flux1-dev-flo-chars:0.4.3
docker push echeg/flux1-dev-flo-objs:0.4.3
```

## Использование готовых образов

```bash
# Скачайте и запустите готовые образы из Docker Hub
docker run -p 8188:8188 echeg/flux1-dev-flo-chars:0.4.3
docker run -p 8189:8188 echeg/flux1-dev-flo-objs:0.4.3
```

## Устранение неполадок

### Ошибка при сборке "No such file or directory"
Убедитесь, что файлы моделей находятся в правильном месте:
```bash
ls -la models/Models/FLO_AI_VectorCharacters_NL_Slow_v2.safetensors
ls -la models/Models/FLO_AI_VectorObjects_NL_Slow_v2.safetensors
```

### Конфликт портов
Если порт 8188 занят, используйте другой порт:
```bash
docker run -p 8190:8188 echeg/flux1-dev-flo-chars:0.4.3
```

### Проверка логов контейнера
```bash
docker logs flo-chars
docker logs flo-objs
```

### Проблемы с платформой на Mac
Если на Mac возникают проблемы с архитектурой ARM, убедитесь, что используете флаг `--platform=linux/amd64`:
```bash
docker build --platform=linux/amd64 -f DockerfileFLOVectorCharacters -t echeg/flux1-dev-flo-chars:0.4.3 .
```

Для запуска также может потребоваться указать платформу:
```bash
docker run --platform=linux/amd64 -p 8188:8188 echeg/flux1-dev-flo-chars:0.4.3
```

## Дополнительные команды

### Остановка контейнеров
```bash
docker stop flo-chars flo-objs
```

### Удаление контейнеров
```bash
docker rm flo-chars flo-objs
```

### Удаление образов
```bash
docker rmi echeg/flux1-dev-flo-chars:0.4.3
docker rmi echeg/flux1-dev-flo-objs:0.4.3
```

### Освобождение дискового пространства
```bash
docker system prune -a
```

## Примечания

- Образы основаны на `echeg/flux1-dev-nodes:0.4.3`
- Старая модель flux1-dev удаляется для экономии места
- Симлинки позволяют использовать модели в различных workflow ComfyUI
- Для production использования рекомендуется использовать конкретные теги версий
- Модели оптимизированы для создания векторных персонажей и объектов
- **Важно**: Используется флаг `--platform=linux/amd64` для принудительной сборки под Linux платформу (предотвращает сборку ARM образов на Mac) 