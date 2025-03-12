import os
import argparse
from google.cloud import storage

# Парсинг аргументов командной строки
parser = argparse.ArgumentParser(description='Загрузка файлов в Google Cloud Storage')
parser.add_argument('--overwrite', action='store_true', help='Перезаписывать существующие файлы')
args = parser.parse_args()

# Указываем путь к сервисному аккаунту (если не настроен в переменной окружения)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/workspace/loremax-6c351a119caa.json"

# Инициализируем клиент
client = storage.Client()
bucket_name = "echeg_model_storage"
bucket = client.bucket(bucket_name)

# Получаем список всех файлов в бакете и их размеры
print("Получение списка файлов в бакете...")
blobs_dict = {}
blobs = bucket.list_blobs()
for blob in blobs:
    blobs_dict[blob.name] = blob.size
    print(blob.name)

# Локальная папка, откуда будем загружать
local_folder = "/workspace/models"

# Префикс в бакете (куда сохранять)
gcs_prefix = "models/"

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
            
        # Создаём путь в бакете относительно `local_folder`
        blob_path = os.path.relpath(local_path, local_folder)
        gcs_path = gcs_prefix + blob_path

        # Проверяем, существует ли файл в бакете и совпадает ли размер
        local_size = os.path.getsize(local_path)
        if gcs_path in blobs_dict and blobs_dict[gcs_path] == local_size and not args.overwrite:
            print(f"Пропускаем {local_path} - файл уже существует в бакете с тем же размером")
            skipped_count += 1
            continue

        # Загружаем файл
        print(f"Загружаем {local_path} → gs://{bucket_name}/{gcs_path}")
        blob = bucket.blob(gcs_path)
        blob.upload_from_filename(local_path)
        uploaded_count += 1

        print(f"Uploaded {local_path} → gs://{bucket_name}/{gcs_path}")

print(f"✅ Загрузка завершена! Загружено: {uploaded_count}, пропущено: {skipped_count}, скрытых директорий пропущено: {hidden_dirs_skipped}")

