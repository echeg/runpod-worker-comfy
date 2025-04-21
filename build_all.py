import os
import sys
import subprocess
import re
from pathlib import Path
import concurrent.futures

# --- CONFIG ---
DOCKERFILES = [
    {
        'file': 'DockerfileNodes',
        'tag': 'echeg/comfyui-nodes-layer',
        'from_pattern': r'^FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04',
        'base_tag': None,  # No version tag for this base
    },
    {
        'file': 'DockerfileBaseModels',
        'tag': 'echeg/comfyui-base-models',
        'from_pattern': r'^FROM echeg/comfyui-nodes-layer:',
        'base_tag': 'echeg/comfyui-nodes-layer',
    },
    {
        'file': 'DockerfileBaseModelsLight',
        'tag': 'echeg/comfyui-base-models-light',
        'from_pattern': r'^FROM echeg/comfyui-base-models:',
        'base_tag': 'echeg/comfyui-base-models',
    },
    {
        'file': 'DockerfileFlux1Dev',
        'tag': 'echeg/comfyui-flux1-dev',
        'from_pattern': r'^FROM echeg/comfyui-base-models:',
        'base_tag': 'echeg/comfyui-base-models',
    },
    {
        'file': 'DockerfileFlux1CannyDev',
        'tag': 'echeg/comfyui-flux1-canny-dev',
        'from_pattern': r'^FROM echeg/comfyui-base-models:',
        'base_tag': 'echeg/comfyui-base-models',
    },
    {
        'file': 'DockerfileFlux1DepthDev',
        'tag': 'echeg/comfyui-flux1-depth-dev',
        'from_pattern': r'^FROM echeg/comfyui-base-models:',
        'base_tag': 'echeg/comfyui-base-models',
    },
    {
        'file': 'DockerfileFlux1FillDev',
        'tag': 'echeg/comfyui-flux1-fill-dev',
        'from_pattern': r'^FROM echeg/comfyui-base-models:',
        'base_tag': 'echeg/comfyui-base-models',
    },
]

PROJECT_ROOT = Path(__file__).parent

def replace_from_version(dockerfile_path, pattern, new_from):
    """Replace FROM ... version in Dockerfile."""
    with open(dockerfile_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    new_lines = []
    replaced = False
    for line in lines:
        if re.match(pattern, line):
            new_lines.append(new_from + '\n')
            replaced = True
        else:
            new_lines.append(line)
    if not replaced:
        raise RuntimeError(f"Pattern '{pattern}' not found in {dockerfile_path}")
    with open(dockerfile_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

def build_image(dockerfile, tag, version):
    print(f"\n--- Building {tag}:{version} from {dockerfile} ---")
    subprocess.run([
        'docker', 'build', '--platform', 'linux/amd64', '-f', dockerfile, '-t', f'{tag}:{version}', '.'
    ], check=True)

def main():
    if len(sys.argv) != 2:
        print("Usage: python build_all.py <version>")
        sys.exit(1)
    version = sys.argv[1]

    # Step 1: Update FROM lines
    for entry in DOCKERFILES:
        dockerfile = str(PROJECT_ROOT / entry['file'])
        if entry['base_tag']:
            new_from = f"FROM {entry['base_tag']}:{version}"
            replace_from_version(dockerfile, entry['from_pattern'], new_from)

    # Step 2: Build images in order
    # Build Nodes, BaseModels, BaseModelsLight последовательно
    for entry in DOCKERFILES[:3]:
        build_image(str(PROJECT_ROOT / entry['file']), entry['tag'], version)

    # Build Flux images параллельно
    flux_entries = DOCKERFILES[3:]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(build_image, str(PROJECT_ROOT / entry['file']), entry['tag'], version)
            for entry in flux_entries
        ]
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as exc:
                print(f"Flux image build generated an exception: {exc}")
                sys.exit(1)

    print("\nAll images built successfully with version:", version)

if __name__ == '__main__':
    main()
