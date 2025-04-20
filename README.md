# Сборка и публикация Docker образов ComfyUI

## 1. Сборка базового слоя (Nodes)

```
docker build -t echeg/comfyui-nodes-layer:0.2.0 --platform linux/amd64 -f DockerfileNodes .
docker push echeg/comfyui-nodes-layer:0.2.0
```

## 2. Сборка базового слоя с моделями (Base Models)

```
docker build -t echeg/comfyui-base-models:0.1.0 --platform linux/amd64 -f DockerfileBaseModels .
docker push echeg/comfyui-base-models:0.1.0
```

### ComfyUI Worker Light

```

docker build -t echeg/comfyui-base-models-light:0.2.1 --platform linux/amd64 -f DockerfileWorker .
docker push echeg/comfyui-base-models-light:0.2.1
```


## 3. Сборка образов с diffusion-моделями

### FLUX.1-dev
```
# Положите flux1-dev.safetensors рядом с DockerfileFlux1Dev (если не хотите скачивать)
docker build -t echeg/comfyui-flux1-dev:0.2.0 --platform linux/amd64 -f DockerfileFlux1Dev .
docker push echeg/comfyui-flux1-dev:0.2.0
```

### FLUX.1-Fill-dev
```
# Положите flux1-fill-dev.safetensors рядом с DockerfileFlux1FillDev (если не хотите скачивать)
docker build -t echeg/comfyui-flux1-fill-dev:0.2.0 --platform linux/amd64 -f DockerfileFlux1FillDev .
docker push echeg/comfyui-flux1-fill-dev:0.2.0
```

### FLUX.1-Depth-dev
```
# Положите flux1-depth-dev.safetensors рядом с DockerfileFlux1DepthDev (если не хотите скачивать)
docker build -t echeg/comfyui-flux1-depth-dev:0.2.0 --platform linux/amd64 -f DockerfileFlux1DepthDev .
docker push echeg/comfyui-flux1-depth-dev:0.2.0
```

### FLUX.1-Canny-dev
```
# Положите flux1-canny-dev.safetensors рядом с DockerfileFlux1CannyDev (если не хотите скачивать)
docker build -t echeg/comfyui-flux1-canny-dev:0.2.0 --platform linux/amd64 -f DockerfileFlux1CannyDev .
docker push echeg/comfyui-flux1-canny-dev:0.2.0
```

## Сборка всех Docker-образов с единой версией

Для сборки всех образов с одной версией используйте скрипт:

```bash
python build_all.py 0.2.3
```

Где `0.2.3` — нужная версия. Скрипт автоматически:
- Подставляет версию во все нужные Dockerfile (FROM ... :<версия>),
- Собирает образы в правильном порядке,
- Тегирует их с нужной версией.

**Требования:**
- Python 3.7+
- Docker

**Порядок сборки:**
1. DockerfileNodes → `echeg/comfyui-nodes-layer:<версия>`
2. DockerfileBaseModels → `echeg/comfyui-base-models:<версия>`
3. DockerfileBaseModelsLight → `echeg/comfyui-base-models-light:<версия>`
4. DockerfileFlux1Dev → `echeg/comfyui-flux1-dev:<версия>`
5. DockerfileFlux1CannyDev → `echeg/comfyui-flux1-canny-dev:<версия>`
6. DockerfileFlux1DepthDev → `echeg/comfyui-flux1-depth-dev:<версия>`
7. DockerfileFlux1FillDev → `echeg/comfyui-flux1-fill-dev:<версия>`

**Пример:**
```bash
python build_all.py 0.2.3
```

Все образы будут иметь тег `:0.2.3`.
