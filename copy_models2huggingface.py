import os
import argparse
from huggingface_hub import HfApi, HfFolder, Repository
from pathlib import Path

# Парсинг аргументов командной строки
parser = argparse.ArgumentParser(description='Загрузка файлов на Hugging Face')
parser.add_argument('--overwrite', action='store_true', help='Перезаписывать существующие файлы')
parser.add_argument('--repo_id', type=str, required=True, help='ID репозитория на Hugging Face (например, username/model-name)')
parser.add_argument('--token', type=str, help='Токен доступа к Hugging Face. Если не указан, будет использован сохраненный токен')
args = parser.parse_args()

# Получаем токен
token = args.token
if not token:
    token = HfFolder.get_token()
    if not token:
        raise ValueError("Токен не указан и не найден в кэше. Используйте --token или выполните 'huggingface-cli login'")

# Инициализируем API
api = HfApi()

# Локальная папка, откуда будем загружать
local_folder = "/workspace/models"

# Получаем список всех файлов в репозитории и их размеры
print(f"Получение списка файлов в репозитории {args.repo_id}...")
try:
    repo_files = api.list_repo_files(repo_id=args.repo_id, token=token)
    
    # Получаем информацию о размерах файлов
    files_info = {}
    for file_path in repo_files:
        try:
            file_info = api.get_info_from_repo(
                repo_id=args.repo_id,
                filename=file_path,
                token=token
            )
            if hasattr(file_info, 'size'):
                files_info[file_path] = file_info.size
            else:
                # Если размер не доступен через API, пропускаем файл
                files_info[file_path] = None
        except Exception as e:
            print(f"Не удалось получить информацию о файле {file_path}: {e}")
            files_info[file_path] = None
    
    print(f"Найдено {len(repo_files)} файлов в репозитории")
except Exception as e:
    print(f"Ошибка при получении списка файлов: {e}")
    # Если репозиторий не существует или другая ошибка, начинаем с пустого списка
    files_info = {}

# Счетчики для статистики
uploaded_count = 0
skipped_count = 0
hidden_dirs_skipped = 0

# Рекурсивный обход файлов
for root, dirs, files in os.walk(local_folder):
    # Фильтруем скрытые директории (начинающиеся с точки)
    # Модифицируем список dirs на месте, чтобы os.walk не заходил в эти директории
    dirs_to_remove = []
    for dir_name in dirs:
        if dir_name.startswith('.'):
            dirs_to_remove.append(dir_name)
            hidden_dirs_skipped += 1
            print(f"Пропускаем скрытую директорию: {os.path.join(root, dir_name)}")
    
    for dir_name in dirs_to_remove:
        dirs.remove(dir_name)
    
    for file in files:
        local_path = os.path.join(root, file)
        
        # Пропускаем символические ссылки
        if os.path.islink(local_path):
            print(f"Пропускаем символическую ссылку: {local_path}")
            continue
            
        # Создаём относительный путь
        rel_path = os.path.relpath(local_path, local_folder)
        
        # Проверяем, существует ли файл в репозитории и совпадает ли размер
        local_size = os.path.getsize(local_path)
        if rel_path in files_info and files_info[rel_path] == local_size and not args.overwrite:
            print(f"Пропускаем {local_path} - файл уже существует в репозитории с тем же размером")
            skipped_count += 1
            continue

        # Загружаем файл
        print(f"Загружаем {local_path} → {args.repo_id}/{rel_path}")
        try:
            api.upload_file(
                path_or_fileobj=local_path,
                path_in_repo=rel_path,
                repo_id=args.repo_id,
                token=token,
                repo_type="model"
            )
            uploaded_count += 1
            print(f"Uploaded {local_path} → {args.repo_id}/{rel_path}")
        except Exception as e:
            print(f"Ошибка при загрузке {local_path}: {e}")

print(f"✅ Загрузка завершена! Загружено: {uploaded_count}, пропущено: {skipped_count}, скрытых директорий пропущено: {hidden_dirs_skipped}") 