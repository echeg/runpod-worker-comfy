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
ADD src/start.sh src/restore_snapshot.sh src/rp_handler.py test_input.json src/model_manager.py src/download_default_models_for_nodes.sh ./
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

# ComfyUI-KJNodes
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/kijai/ComfyUI-KJNodes.git && \
    cd ComfyUI-KJNodes && \
    git checkout 3f141b8f1ca1c832a1c6accd806f2d2f40fd4075 && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# ComfyUI-RMBG
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/1038lab/ComfyUI-RMBG.git && \
    cd ComfyUI-RMBG && \
    git checkout 919fecfd6dbd5caf51543561ad1b1e69e1170a16 && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# ComfyUI_essentials
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/cubiq/ComfyUI_essentials.git && \
    cd ComfyUI_essentials && \
    git checkout 33ff89fd354d8ec3ab6affb605a79a931b445d99 && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# ComfyUI_UltimateSDUpscale
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/ssitu/ComfyUI_UltimateSDUpscale.git --recursive && \
    cd ComfyUI_UltimateSDUpscale && \
    git checkout ff3fdfeee03de46d4462211cffd165d27155e858 && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# ComfyUI-Impact-Pack
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack.git && \
    cd ComfyUI-Impact-Pack && \
    git checkout d8738eee2f6c8c9a17ca42ab71f47ce35ccca3e7 && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# ComfyUI-Easy-Use
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/yolain/ComfyUI-Easy-Use.git && \
    cd ComfyUI-Easy-Use && \
    git checkout 65937a75ebdbe5c35afe6474dfe12673aca5f0ac && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi
  
# ComfyUI-QualityOfLifeSuit_Omar92
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/omar92/ComfyUI-QualityOfLifeSuit_Omar92.git && \
    cd ComfyUI-QualityOfLifeSuit_Omar92 && \
    git checkout f09d10dea0afbd3984a284acf8f0913a634e36ec && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# ComfyUI-SAMURAI--SAM2-
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/takemetosiberia/ComfyUI-SAMURAI--SAM2-.git && \
    cd ComfyUI-SAMURAI--SAM2- && \
    git checkout 42b13f2e4f859f9da058efb407d3aeede8a4f6ce && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# ComfyUI-segment-anything-2
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/kijai/ComfyUI-segment-anything-2.git && \
    cd ComfyUI-segment-anything-2 && \
    git checkout 059815ecc55b17ae9b47d15ed9b39b243d73b25f && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Comfyui_controlnet_aux
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/Fannovel16/comfyui_controlnet_aux.git && \
    cd comfyui_controlnet_aux && \
    git checkout 5a049bde9cc117dafc327cded156459289097ea1 && \
    pip install --no-cache-dir -r requirements.txt;
    
# Bedrock - Claude Multimodal
#RUN cd /comfyui/custom_nodes && \
#    git clone https://github.com/aws-samples/comfyui-llm-node-for-amazon-bedrock.git && \
#    cd comfyui-llm-node-for-amazon-bedrock && \
#    git checkout 30fd153e98b40b2df628e0141914cae245d73ff3 && \
#    pip install --no-cache-dir -r requirements.txt;

RUN pip install --no-cache-dir google-cloud-storage huggingface_hub boto3
    
# Create web/extensions directory
RUN mkdir -p /comfyui/web/extensions

# Comfyui-ergouzi-Nodes
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/11dogzi/Comfyui-ergouzi-Nodes.git && \
    cd Comfyui-ergouzi-Nodes && \
    git checkout 0d6ac29773fa03e439dd9deb282453b739403427 && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# ComfyUI-Florence2
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/kijai/ComfyUI-Florence2.git && \
    cd ComfyUI-Florence2 && \
    git checkout dffd12506d50f0540b8a7f4b36a05d4fb5fed2de && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# ComfyUI-Fluxtapoz
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/logtd/ComfyUI-Fluxtapoz.git && \
    cd ComfyUI-Fluxtapoz && \
    git checkout 17c71bea20e932945e9c1be0586cfd4b7e51cbf6 && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# ComfyUI-GGUF
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/city96/ComfyUI-GGUF.git && \
    cd ComfyUI-GGUF && \
    git checkout 5875c52f59baca3a9372d68c43a3775e21846fe0 && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Comfyui-In-Context-Lora-Utils
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/lrzjason/Comfyui-In-Context-Lora-Utils.git && \
    cd Comfyui-In-Context-Lora-Utils && \
    git checkout 6ef772d589928a380a139c6cd2cfc49b83c8e441 && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# ComfyUI-Inpaint-CropAndStitch
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/lquesada/ComfyUI-Inpaint-CropAndStitch.git && \
    cd ComfyUI-Inpaint-CropAndStitch && \
    git checkout 2abf837822d761110ac383d9a1cdffcc7ebfab36 && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Start container
CMD ["/start.sh"]
