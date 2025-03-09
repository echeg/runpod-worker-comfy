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

# Install nginx
RUN apt-get update && \
apt-get install -y nginx

# Create necessary directories and copy necessary files
RUN mkdir -p /usr/share/nginx/html

# NGINX Proxy
COPY build-context/nginx.conf /etc/nginx/nginx.conf
COPY build-context/readme.html /usr/share/nginx/html/readme.html

# Copy the README.md
COPY README.md /usr/share/nginx/html/README.md

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

# Install paddlepaddle paddleocr
RUN pip install --no-cache-dir paddlepaddle paddleocr

# Install custom nodes with their requirements

# cg-use-everywhere
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/chrisgoringe/cg-use-everywhere.git && \
    cd cg-use-everywhere && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# ComfyMath
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/evanspearman/ComfyMath.git && \
    cd ComfyMath && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# comfyui-art-venture
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/sipherxyz/comfyui-art-venture.git && \
    cd comfyui-art-venture && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# ComfyUI-BRIA_AI-RMBG
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/ZHO-ZHO-ZHO/ComfyUI-BRIA_AI-RMBG.git && \
    cd ComfyUI-BRIA_AI-RMBG && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# ComfyUI-ControlnetAux
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/madtunebk/ComfyUI-ControlnetAux.git && \
    cd ComfyUI-ControlnetAux && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# ComfyUI-Custom-Scripts
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/pythongosssss/ComfyUI-Custom-Scripts.git && \
    cd ComfyUI-Custom-Scripts && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# ComfyUI-Easy-Use
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/yolain/ComfyUI-Easy-Use.git && \
    cd ComfyUI-Easy-Use && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Comfyui-ergouzi-Nodes
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/11dogzi/Comfyui-ergouzi-Nodes.git && \
    cd Comfyui-ergouzi-Nodes && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

RUN mkdir -p /comfyui/web/extensions/EG_GN_NODES

# ComfyUI-Florence2
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/kijai/ComfyUI-Florence2.git && \
    cd ComfyUI-Florence2 && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# ComfyUI-Fluxtapoz
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/logtd/ComfyUI-Fluxtapoz.git && \
    cd ComfyUI-Fluxtapoz && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# ComfyUI-GGUF
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/city96/ComfyUI-GGUF.git && \
    cd ComfyUI-GGUF && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# ComfyUI-Impact-Pack
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack.git && \
    cd ComfyUI-Impact-Pack && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Comfyui-In-Context-Lora-Utils
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/lrzjason/Comfyui-In-Context-Lora-Utils.git && \
    cd Comfyui-In-Context-Lora-Utils && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# ComfyUI-Inpaint-CropAndStitch
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/lquesada/ComfyUI-Inpaint-CropAndStitch.git && \
    cd ComfyUI-Inpaint-CropAndStitch && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# comfyui-inpaint-nodes
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/Acly/comfyui-inpaint-nodes.git && \
    cd comfyui-inpaint-nodes && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# ComfyUI-KJNodes
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/kijai/ComfyUI-KJNodes.git && \
    cd ComfyUI-KJNodes && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# comfyui-lama-remover
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/Layer-norm/comfyui-lama-remover.git && \
    cd comfyui-lama-remover && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# comfyui-llm-node-for-amazon-bedrock
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/aws-samples/comfyui-llm-node-for-amazon-bedrock.git && \
    cd comfyui-llm-node-for-amazon-bedrock && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# ComfyUI-Logic
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/theUpsider/ComfyUI-Logic.git && \
    cd ComfyUI-Logic && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# comfyui-mixlab-nodes
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/shadowcz007/comfyui-mixlab-nodes.git && \
    cd comfyui-mixlab-nodes && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# comfyui-photoshop
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/NimaNzrii/comfyui-photoshop.git && \
    cd comfyui-photoshop && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# ComfyUI-QualityOfLifeSuit_Omar92
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/omar92/ComfyUI-QualityOfLifeSuit_Omar92.git && \
    cd ComfyUI-QualityOfLifeSuit_Omar92 && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# ComfyUI-RMBG
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/1038lab/ComfyUI-RMBG.git && \
    cd ComfyUI-RMBG && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# ComfyUI-SAMURAI--SAM2-
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/takemetosiberia/ComfyUI-SAMURAI--SAM2-.git && \
    cd ComfyUI-SAMURAI--SAM2- && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# ComfyUI-segment-anything-2
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/kijai/ComfyUI-segment-anything-2.git && \
    cd ComfyUI-segment-anything-2 && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# comfyui-tensorops
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/un-seen/comfyui-tensorops.git && \
    cd comfyui-tensorops && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# ComfyUI_AdvancedRefluxControl
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/kaibioinfo/ComfyUI_AdvancedRefluxControl.git && \
    cd ComfyUI_AdvancedRefluxControl && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# ComfyUI_Comfyroll_CustomNodes
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/Suzie1/ComfyUI_Comfyroll_CustomNodes.git && \
    cd ComfyUI_Comfyroll_CustomNodes && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# comfyui_controlnet_aux
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/Fannovel16/comfyui_controlnet_aux.git && \
    cd comfyui_controlnet_aux && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# ComfyUI_essentials
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/cubiq/ComfyUI_essentials.git && \
    cd ComfyUI_essentials && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Comfyui_JC2
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/TTPlanetPig/Comfyui_JC2.git && \
    cd Comfyui_JC2 && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# ComfyUI_JPS-Nodes
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/JPS-GER/ComfyUI_JPS-Nodes.git && \
    cd ComfyUI_JPS-Nodes && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# ComfyUI_LayerStyle
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/chflame163/ComfyUI_LayerStyle.git && \
    cd ComfyUI_LayerStyle && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# ComfyUI_LayerStyle_Advance
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/chflame163/ComfyUI_LayerStyle_Advance.git && \
    cd ComfyUI_LayerStyle_Advance && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Comfyui_Object_Migration
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/TTPlanetPig/Comfyui_Object_Migration.git && \
    cd Comfyui_Object_Migration && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Comfyui_TTP_Toolset
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/TTPlanetPig/Comfyui_TTP_Toolset.git && \
    cd Comfyui_TTP_Toolset && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# ComfyUI_UltimateSDUpscale
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/ssitu/ComfyUI_UltimateSDUpscale.git && \
    cd ComfyUI_UltimateSDUpscale && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# efficiency-nodes-comfyui
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/jags111/efficiency-nodes-comfyui.git && \
    cd efficiency-nodes-comfyui && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# mikey_nodes
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/bash-j/mikey_nodes.git && \
    cd mikey_nodes && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# was-node-suite-comfyui
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/WASasquatch/was-node-suite-comfyui.git && \
    cd was-node-suite-comfyui && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# rgthree-comfy
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/rgthree/rgthree-comfy.git && \
    cd rgthree-comfy && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# x-flux-comfyui
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/XLabs-AI/x-flux-comfyui.git && \
    cd x-flux-comfyui && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Install notebook
RUN pip install --no-cache-dir notebook==6.5.5

# Support for the network volume
ADD src/extra_model_paths.yaml ./

# Go back to the root
WORKDIR /

# Add scripts
ADD src/start.sh src/restore_snapshot.sh src/rp_handler.py test_input.json ./
RUN chmod +x /start.sh /restore_snapshot.sh

# Optionally copy the snapshot file
ADD *snapshot*.json /

# Restore the snapshot to install custom nodes
RUN /restore_snapshot.sh

# Start container
CMD ["/start.sh"]
