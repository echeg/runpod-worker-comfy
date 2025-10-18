import subprocess
import os
import argparse

# Список моделей (имя файла)
MODELS = [
    "flux1-dev.safetensors",
    "flux1-canny-dev.safetensors",
    "flux1-depth-dev.safetensors",
    "flux1-fill-dev.safetensors",
]

# Шаги сборки: (имя Dockerfile, суффикс для тега)
STEPS = [
    ("Dockerfile.BaseModel", "base"),
    ("Dockerfile.System",    "system"),
    ("Dockerfile.Nodes",     "nodes"),
    ("Dockerfile.Models",    "models"),
    ("Dockerfile.Worker",    "worker"),
]

DOCKERIGNORE_PATH = ".dockerignore"
ORIGINAL_DOCKERIGNORE = None

def load_original_dockerignore():
    global ORIGINAL_DOCKERIGNORE
    if ORIGINAL_DOCKERIGNORE is None and os.path.exists(DOCKERIGNORE_PATH):
        with open(DOCKERIGNORE_PATH, 'r', encoding='utf-8') as f:
            ORIGINAL_DOCKERIGNORE = f.read()

def write_dockerignore_for(model_file: str):
    """
    Перезаписывает .dockerignore так, чтобы в контексте оставался только один файл модели.
    """
    load_original_dockerignore()
    lines = [
        "**/*",                    # игнорируем всё
        "!Dockerfile.*",           # оставляем Dockerfile'ы
        f"!models/diffusion_models/{model_file}",  # и текущую модель
    ]
    with open(DOCKERIGNORE_PATH, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines) + "\n")
    print(f"[INFO] .dockerignore обновлён для {model_file}")

def restore_original_dockerignore():
    """
    Восстанавливает исходный .dockerignore.
    """
    if ORIGINAL_DOCKERIGNORE is not None:
        with open(DOCKERIGNORE_PATH, 'w', encoding='utf-8') as f:
            f.write(ORIGINAL_DOCKERIGNORE)
        print("[INFO] .dockerignore восстановлён")

def image_exists(tag: str) -> bool:
    """Проверяет наличие локального образа по тегу."""
    return subprocess.call(
        ["docker", "image", "inspect", tag],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    ) == 0

def build_image(dockerfile: str, context: str, tag: str, build_args: dict):
    """Собирает Docker-образ, если он ещё не существует."""
    if image_exists(tag):
        print(f"[SKIP] {tag} уже есть")
        return
    cmd = ["docker", "build", "-f", dockerfile, "-t", tag]
    for k, v in build_args.items():
        cmd += ["--build-arg", f"{k}={v}"]
    cmd.append(context)
    print(f"[BUILD] {tag} из {dockerfile} ...")
    subprocess.check_call(cmd)
    print(f"[OK] Образ {tag} построен")

def push_image(tag: str):
    """Пушит Docker-образ в реестр."""
    print(f"[PUSH] Отправка {tag} ...")
    subprocess.check_call(["docker", "push", tag])
    print(f"[OK] Образ {tag} запушен")

def build_sequence(model_file: str, version: str, do_build: bool, do_push: bool):
    """
    Для модели: обновляет .dockerignore, затем по шагам собирает и/или пушит образы.
    """
    name = os.path.splitext(model_file)[0]
    previous_tag = None

    write_dockerignore_for(model_file)
    try:
        for dockerfile, suffix in STEPS:
            tag = f"echeg/default-{name}-{suffix}:{version}"
            build_args = {"VERSION": version}
            if suffix == "base":
                build_args["MODEL_FILE"] = model_file
            else:
                build_args["BASE_IMAGE"] = previous_tag

            if do_build:
                build_image(dockerfile, ".", tag, build_args)
            if do_push:
                push_image(tag)

            previous_tag = tag
    finally:
        restore_original_dockerignore()

def parse_args():
    parser = argparse.ArgumentParser(
        description="Скрипт для сборки и пуша Docker-образов моделей"
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--build-only", action="store_true",
        help="только собрать образы, без пуша"
    )
    group.add_argument(
        "--push-only", action="store_true",
        help="только запушить существующие образы"
    )
    # если ни build-only, ни push-only, то по умолчанию оба
    parser.add_argument(
        "-v", "--version", default="0.2",
        help="версия (тег) для образов"
    )
    return parser.parse_args()

def main():
    args = parse_args()
    do_build = not args.push_only
    do_push = not args.build_only
    print(f"Настройка: build={'yes' if do_build else 'no'}, push={'yes' if do_push else 'no'}")
    for model in MODELS:
        try:
            build_sequence(model, args.version, do_build, do_push)
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Сбой при обработке {model}: {e}")
            break

if __name__ == "__main__":
    main()