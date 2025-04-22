import subprocess
from pathlib import Path
import tempfile
import argparse

PROJECT_ROOT = Path(__file__).parent

FLUX_VARIANTS = [
    {
        'name': 'echeg/df2/flux1-dev-nodes',
        'flux_dockerfile': 'DF2_FluxDevModel',
        'flux_tag': 'echeg/df2/flux1-dev',
    },
    {
        'name': 'echeg/df2/flux1-canny-nodes',
        'flux_dockerfile': 'DF2_FluxCannyDevModel',
        'flux_tag': 'echeg/df2/flux1-canny-dev',
    },
    {
        'name': 'echeg/df2/flux1-depth-nodes',
        'flux_dockerfile': 'DF2_FluxDepthDevModel',
        'flux_tag': 'echeg/df2/flux1-depth-dev',
    },
    {
        'name': 'echeg/df2/flux1-fill-nodes',
        'flux_dockerfile': 'DF2_FluxFillDevModel',
        'flux_tag': 'echeg/df2/flux1-fill-dev',
    },
]

SHARED_DOCKERFILE = 'DF2_Shared'

def image_exists(tag):
    result = subprocess.run(['docker', 'image', 'inspect', tag], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return result.returncode == 0

def patch_from(dockerfile_path, new_from, temp_dir):
    with open(dockerfile_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if line.strip().startswith('FROM '):
            lines[i] = f'FROM {new_from}\n'
            break
    temp_dockerfile = Path(temp_dir) / Path(dockerfile_path).name
    with open(temp_dockerfile, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    return str(temp_dockerfile)

def build_image(dockerfile, tag):
    print(f"\n--- Building {tag} from {dockerfile} ---")
    subprocess.run([
        'docker', 'build', '--platform', 'linux/amd64', '-f', dockerfile, '-t', tag, '.'
    ], check=True)

def main():
    parser = argparse.ArgumentParser(description='DF2 build with per-layer versioning')
    parser.add_argument('--flux', default='latest', help='Flux image version')
    parser.add_argument('--shared', default='latest', help='Shared image version')
    args = parser.parse_args()

    results = []
    with tempfile.TemporaryDirectory() as temp_dir:
        for variant in FLUX_VARIANTS:
            # 1. Build flux image
            flux_tag = f"{variant['flux_tag']}:{args.flux}"
            if image_exists(flux_tag):
                print(f"Образ {flux_tag} уже существует, пропускаем сборку.")
            else:
                build_image(str(PROJECT_ROOT / variant['flux_dockerfile']), flux_tag)
            # 2. Patch and build shared
            shared_tag = f"{variant['name']}:{args.shared}"
            if image_exists(shared_tag):
                print(f"Образ {shared_tag} уже существует, пропускаем сборку.")
            else:
                patched_shared = patch_from(str(PROJECT_ROOT / SHARED_DOCKERFILE), flux_tag, temp_dir)
                build_image(patched_shared, shared_tag)

            results.append({
                'flux': flux_tag,
                'shared': shared_tag
            })
    print("\nВсе образы успешно собраны (или были уже собраны ранее):")
    for r in results:
        print(f"Flux:   {r['flux']}")
        print(f"Shared: {r['shared']}")
        print('---')

if __name__ == '__main__':
    main()
