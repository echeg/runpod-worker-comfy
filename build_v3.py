import subprocess
from pathlib import Path
import tempfile
import argparse
import os

# Конфигурация вариантов и базовых образов
VARIANTS = {
    'flux1-dev': 'echeg/flux1-dev',
    'flux1-canny-dev': 'echeg/flux1-canny-dev',
    'flux1-depth-dev': 'echeg/flux1-depth-dev',
    'flux1-fill-dev': 'echeg/flux1-fill-dev',
}

SHARED_DOCKERFILE = Path('DF2_Shared')
OUTPUT_TAG_SUFFIX = 'shared'


def image_exists(tag):
    result = subprocess.run(['docker', 'image', 'inspect', tag], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return result.returncode == 0


def patch_dockerfile(base_lines, new_from, dest_path):
    lines = base_lines.copy()
    for i, line in enumerate(lines):
        if line.strip().startswith('FROM '):
            lines[i] = f'FROM {new_from}\n'
            break
    with open(dest_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)


def build_variant(variant, base_repo, version, shared_lines, tag_suffix, keep_files=False, skip=False):
    base_from = f"{base_repo}:0.4.1"
    tag = f"{base_repo}-{tag_suffix}:{version}"

    if not skip and image_exists(tag):
        print(f"Образ {tag} уже существует. Пропускаем.")
        return

    if keep_files or skip:
        Path("dockerfiles").mkdir(exist_ok=True)
        dockerfile_path = Path("dockerfiles") / f"Dockerfile.{variant}"
    else:
        temp_dir = tempfile.TemporaryDirectory()
        dockerfile_path = Path(temp_dir.name) / f"Dockerfile.{variant}"

    patch_dockerfile(shared_lines, base_from, dockerfile_path)
    print(f"\nDockerfile для {variant} сохранён в {dockerfile_path}")

    if not skip:
        print(f"--- Сборка {tag} ---")
        try:
            subprocess.run([
                'docker', 'build', '--platform', 'linux/amd64', '-f', str(dockerfile_path), '-t', tag, '.'
            ], check=True)
        finally:
            if not keep_files:
                temp_dir.cleanup()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', default='latest', help='Тег версии (по умолчанию: latest)')
    parser.add_argument('--keep-dockerfiles', action='store_true', help='Сохранять Dockerfile в ./dockerfiles')
    parser.add_argument('--skip', action='store_true', help='Только генерировать Dockerfile (без сборки)')
    args = parser.parse_args()

    with open(SHARED_DOCKERFILE, 'r', encoding='utf-8') as f:
        shared_lines = f.readlines()

    for variant, base_repo in VARIANTS.items():
        try:
            build_variant(
                variant, base_repo, args.version,
                shared_lines, OUTPUT_TAG_SUFFIX,
                keep_files=args.keep_dockerfiles or args.skip,
                skip=args.skip
            )
        except subprocess.CalledProcessError as e:
            print(f"Ошибка при сборке {variant}: {e}")


if __name__ == '__main__':
    main()
