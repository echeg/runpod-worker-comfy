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

---
