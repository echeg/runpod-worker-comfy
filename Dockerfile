# Stage 1: Base image with common dependencies
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04 as base

# Prevents prompts from packages asking for user input during installation
ENV DEBIAN_FRONTEND=noninteractive
# Prefer binary wheels over source distributions for faster pip installations
ENV PIP_PREFER_BINARY=1
# Ensures output from python is printed immediately to the terminal without buffering
ENV PYTHONUNBUFFERED=1 
# Speed up some cmake builds
ENV CMAKE_BUILD_PARALLEL_LEVEL=8

# Install Python, git and other necessary tools
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    git \
    wget \
    libglib2.0-0 libsm6 libgl1 libxrender1 libxext6 \
    && ln -sf /usr/bin/python3.10 /usr/bin/python \
    && ln -sf /usr/bin/pip3 /usr/bin/pip

# Clean up to reduce image size
RUN apt-get autoremove -y && apt-get clean -y && rm -rf /var/lib/apt/lists/*

# Install comfy-cli
RUN pip install --no-cache-dir comfy-cli

# Install ComfyUI
RUN /usr/bin/yes | comfy --workspace /comfyui install --cuda-version 11.8 --nvidia --version 0.3.26

# Change working directory to ComfyUI
WORKDIR /comfyui

# Install runpod
RUN pip install --no-cache-dir runpod requests

# Support for the network volume
ADD src/extra_model_paths.yaml ./

# Install PaddleOCR
RUN pip install --no-cache-dir paddlepaddle paddleocr

# Go back to the root
WORKDIR /

# Add scripts
ADD src/start.sh src/restore_snapshot.sh src/rp_handler.py test_input.json ./
RUN chmod +x /start.sh /restore_snapshot.sh

# Optionally copy the snapshot file
ADD *snapshot*.json /

# Restore the snapshot to install custom nodes
RUN /restore_snapshot.sh

# Install JupyterLab
RUN pip install --no-cache-dir jupyterlab

# Установка custom nodes для ComfyUI

# cg-use-everywhere
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/chrisgoringe/cg-use-everywhere.git && \
    cd cg-use-everywhere && \
    git checkout ce510b97d10e69d5fd0042e115ecd946890d2079 && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# ComfyMath
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/evanspearman/ComfyMath.git && \
    cd ComfyMath && \
    git checkout 939bb813f1c0ace959b62f20bb2da47190c4e211 && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# comfyui-art-venture
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/sipherxyz/comfyui-art-venture.git && \
    cd comfyui-art-venture && \
    git checkout 50abaace756b96f5f5dc2c9d72826ef371afd45e && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# ComfyUI-BRIA_AI-RMBG
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/ZHO-ZHO-ZHO/ComfyUI-BRIA_AI-RMBG.git && \
    cd ComfyUI-BRIA_AI-RMBG && \
    git checkout 827fcd63ff0cfa7fbc544b8d2f4c1e3f3012742d && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# ComfyUI-Custom-Scripts
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/pythongosssss/ComfyUI-Custom-Scripts.git && \
    cd ComfyUI-Custom-Scripts && \
    git checkout bc8922deff73f59311c05cef27b9d4caaf43e87b && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# was-node-suite-comfyui
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/WASasquatch/was-node-suite-comfyui.git && \
    cd was-node-suite-comfyui && \
    git checkout 056badacda52e88d29d6a65f9509cd3115ace0f2 && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# rgthree-comfy
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/rgthree/rgthree-comfy.git && \
    cd rgthree-comfy && \
    git checkout 5d771b8b56a343c24a26e8cea1f0c87c3d58102f && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# x-flux-comfyui
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/XLabs-AI/x-flux-comfyui.git && \
    cd x-flux-comfyui && \
    git checkout 00328556efc9472410d903639dc9e68a8471f7ac && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi


# ComfyUI_Comfyroll_CustomNodes
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/Suzie1/ComfyUI_Comfyroll_CustomNodes.git && \
    cd ComfyUI_Comfyroll_CustomNodes && \
    git checkout d78b780ae43fcf8c6b7c6505e6ffb4584281ceca && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# comfyui-mixlab-nodes
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/shadowcz007/comfyui-mixlab-nodes.git && \
    cd comfyui-mixlab-nodes && \
    git checkout 67c974c96e6472316cb4bf4326281d9f86a25ae6 && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Start container
CMD ["/start.sh"]
