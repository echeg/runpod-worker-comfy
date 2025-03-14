import os
import sys
import argparse

class ModelManager:
    def __init__(self):
        # Парсинг аргументов командной строки
        parser = argparse.ArgumentParser(
            description='Универсальная загрузка и скачивание файлов с облачных хранилищ'
        )
        parser.add_argument(
            '--action',
            type=str,
            default='upload',
            choices=['upload', 'download'],
            help='Действие: upload (загрузка на облако) или download (скачивание с облака)'
        )
        parser.add_argument(
            '--storage', type=str, required=True, choices=['google', 'huggingface', 's3'],
            help='Тип хранилища (google, huggingface, s3)'
        )
        parser.add_argument(
            '--overwrite', action='store_true',
            help='Перезаписывать существующие файлы'
        )
        parser.add_argument(
            '--local_folder', type=str, default="/workspace/models",
            help='Локальная папка с моделями'
        )

        # Аргументы для Google Cloud Storage
        parser.add_argument('--gcs_bucket', type=str, help='Имя бакета Google Cloud Storage')
        parser.add_argument('--gcs_prefix', type=str, default="models/",
                            help='Префикс в бакете Google Cloud Storage')
        parser.add_argument('--gcs_credentials', type=str,
                            help='Путь к файлу учетных данных Google Cloud')

        # Аргументы для Hugging Face
        parser.add_argument('--hf_repo_id', type=str,
                            help='ID репозитория на Hugging Face (например, username/model-name)')
        parser.add_argument('--hf_token', type=str,
                            help='Токен доступа к Hugging Face')

        # Аргументы для AWS S3
        parser.add_argument('--s3_bucket', type=str, help='Имя бакета S3')
        parser.add_argument('--s3_prefix', type=str, default="models/",
                            help='Префикс в бакете S3')
        parser.add_argument('--s3_region', type=str, default="us-east-1",
                            help='Регион AWS')
        parser.add_argument('--s3_access_key', type=str, help='AWS Access Key ID')
        parser.add_argument('--s3_secret_key', type=str, help='AWS Secret Access Key')

        self.args = parser.parse_args()

        # Счетчики для статистики
        self.uploaded_count = 0
        self.skipped_count = 0
        self.hidden_dirs_skipped = 0

    def walk_files(self, local_folder):
        """
        Генератор для обхода файлов в папке с исключением скрытых директорий и символических ссылок.
        Также исключаются файлы размером меньше 100 КБ.
        """
        MIN_FILE_SIZE = 100 * 1024  # 100 КБ в байтах
        
        for root, dirs, files in os.walk(local_folder):
            for dir_name in dirs.copy():
                if dir_name.startswith('.'):
                    self.hidden_dirs_skipped += 1
                    print(f"Пропускаем скрытую директорию: {os.path.join(root, dir_name)}")
                    dirs.remove(dir_name)
            for file in files:
                local_path = os.path.join(root, file)
                if os.path.islink(local_path):
                    print(f"Пропускаем символическую ссылку: {local_path}")
                    continue
                    
                # Проверка размера файла
                file_size = os.path.getsize(local_path)
                if file_size < MIN_FILE_SIZE:
                    print(f"Пропускаем {local_path} - файл меньше 100 КБ ({file_size / 1024:.2f} КБ)")
                    continue
                    
                rel_path = os.path.relpath(local_path, local_folder)
                yield local_path, rel_path

    # ============================
    # Методы загрузки на облако
    # ============================
    def upload_to_google(self):
        try:
            from google.cloud import storage
        except ImportError:
            print("Ошибка: Для работы с Google Cloud Storage необходимо установить библиотеку google-cloud-storage")
            print("Выполните: pip install google-cloud-storage")
            sys.exit(1)
        
        if not self.args.gcs_bucket:
            print("Ошибка: Для Google Cloud Storage необходимо указать имя бакета (--gcs_bucket)")
            sys.exit(1)
        
        if self.args.gcs_credentials:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.args.gcs_credentials
        
        client = storage.Client()
        bucket_name = self.args.gcs_bucket
        bucket = client.bucket(bucket_name)
        
        print(f"Получение списка файлов в бакете {bucket_name}...")
        blobs_dict = {}
        blobs = bucket.list_blobs(prefix=self.args.gcs_prefix)
        for blob in blobs:
            blobs_dict[blob.name] = blob.size
        
        print(f"Найдено {len(blobs_dict)} файлов в бакете")
        
        for local_path, rel_path in self.walk_files(self.args.local_folder):
            gcs_path = self.args.gcs_prefix + rel_path
            local_size = os.path.getsize(local_path)
            if gcs_path in blobs_dict and blobs_dict[gcs_path] == local_size and not self.args.overwrite:
                print(f"Пропускаем {local_path} - файл уже существует в бакете с тем же размером")
                self.skipped_count += 1
                continue
            
            print(f"Загружаем {local_path} → gs://{bucket_name}/{gcs_path}")
            blob = bucket.blob(gcs_path)
            blob.upload_from_filename(local_path)
            self.uploaded_count += 1
            print(f"Uploaded {local_path} → gs://{bucket_name}/{gcs_path}")

    def upload_to_huggingface(self):
        try:
            from huggingface_hub import HfApi, HfFolder
        except ImportError:
            print("Ошибка: Для работы с Hugging Face необходимо установить библиотеку huggingface_hub")
            print("Выполните: pip install huggingface_hub")
            sys.exit(1)
        
        if not self.args.hf_repo_id:
            print("Ошибка: Для Hugging Face необходимо указать ID репозитория (--hf_repo_id)")
            sys.exit(1)
        
        token = self.args.hf_token
        if not token:
            token = HfFolder.get_token()
            if not token:
                print("Ошибка: Токен Hugging Face не указан и не найден в кэше.")
                print("Используйте --hf_token или выполните 'huggingface-cli login'")
                sys.exit(1)
        
        api = HfApi()
        print(f"Получение списка файлов в репозитории {self.args.hf_repo_id}...")
        try:
            repo_files = api.list_repo_files(repo_id=self.args.hf_repo_id, token=token)
            files_info = {}
            for file_path in repo_files:
                try:
                    file_info = api.get_info_from_repo(
                        repo_id=self.args.hf_repo_id,
                        filename=file_path,
                        token=token
                    )
                    if hasattr(file_info, 'size'):
                        files_info[file_path] = file_info.size
                    else:
                        files_info[file_path] = None
                except Exception as e:
                    print(f"Не удалось получить информацию о файле {file_path}: {e}")
                    files_info[file_path] = None
            print(f"Найдено {len(repo_files)} файлов в репозитории")
        except Exception as e:
            print(f"Ошибка при получении списка файлов: {e}")
            files_info = {}
        
        for local_path, rel_path in self.walk_files(self.args.local_folder):
            local_size = os.path.getsize(local_path)
            if rel_path in files_info and files_info[rel_path] == local_size and not self.args.overwrite:
                print(f"Пропускаем {local_path} - файл уже существует в репозитории с тем же размером")
                self.skipped_count += 1
                continue
            
            print(f"Загружаем {local_path} → {self.args.hf_repo_id}/{rel_path}")
            try:
                api.upload_file(
                    path_or_fileobj=local_path,
                    path_in_repo=rel_path,
                    repo_id=self.args.hf_repo_id,
                    token=token,
                    repo_type="model"
                )
                self.uploaded_count += 1
                print(f"Uploaded {local_path} → {self.args.hf_repo_id}/{rel_path}")
            except Exception as e:
                print(f"Ошибка при загрузке {local_path}: {e}")

    def upload_to_s3(self):
        try:
            import boto3
        except ImportError:
            print("Ошибка: Для работы с AWS S3 необходимо установить библиотеку boto3")
            print("Выполните: pip install boto3")
            sys.exit(1)
        
        if not self.args.s3_bucket:
            print("Ошибка: Для AWS S3 необходимо указать имя бакета (--s3_bucket)")
            sys.exit(1)
        
        s3_kwargs = {'region_name': self.args.s3_region}
        if self.args.s3_access_key and self.args.s3_secret_key:
            s3_kwargs['aws_access_key_id'] = self.args.s3_access_key
            s3_kwargs['aws_secret_access_key'] = self.args.s3_secret_key
        
        s3 = boto3.client('s3', **s3_kwargs)
        
        print(f"Получение списка файлов в бакете S3 {self.args.s3_bucket}...")
        s3_files = {}
        try:
            paginator = s3.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=self.args.s3_bucket, Prefix=self.args.s3_prefix)
            for page in pages:
                if 'Contents' in page:
                    for obj in page['Contents']:
                        s3_files[obj['Key']] = obj['Size']
            print(f"Найдено {len(s3_files)} файлов в бакете S3")
        except Exception as e:
            print(f"Ошибка при получении списка файлов из S3: {e}")
            s3_files = {}
        
        for local_path, rel_path in self.walk_files(self.args.local_folder):
            s3_path = self.args.s3_prefix + rel_path
            local_size = os.path.getsize(local_path)
            if s3_path in s3_files and s3_files[s3_path] == local_size and not self.args.overwrite:
                print(f"Пропускаем {local_path} - файл уже существует в S3 с тем же размером")
                self.skipped_count += 1
                continue
            
            print(f"Загружаем {local_path} → s3://{self.args.s3_bucket}/{s3_path}")
            try:
                s3.upload_file(local_path, self.args.s3_bucket, s3_path)
                self.uploaded_count += 1
                print(f"Uploaded {local_path} → s3://{self.args.s3_bucket}/{s3_path}")
            except Exception as e:
                print(f"Ошибка при загрузке {local_path} в S3: {e}")

    # ================================
    # Методы скачивания с облака
    # ================================
    def download_from_google(self):
        try:
            from google.cloud import storage
        except ImportError:
            print("Ошибка: Для работы с Google Cloud Storage необходимо установить библиотеку google-cloud-storage")
            print("Выполните: pip install google-cloud-storage")
            sys.exit(1)
        
        if not self.args.gcs_bucket:
            print("Ошибка: Для Google Cloud Storage необходимо указать имя бакета (--gcs_bucket)")
            sys.exit(1)
        
        if self.args.gcs_credentials:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.args.gcs_credentials
        
        client = storage.Client()
        bucket_name = self.args.gcs_bucket
        bucket = client.bucket(bucket_name)
        
        print(f"Получение списка файлов в бакете {bucket_name} с префиксом {self.args.gcs_prefix}...")
        blobs = bucket.list_blobs(prefix=self.args.gcs_prefix)
        
        for blob in blobs:
            if not blob.name.startswith(self.args.gcs_prefix):
                continue
            # Вычисляем относительный путь
            rel_path = blob.name[len(self.args.gcs_prefix):]
            local_path = os.path.join(self.args.local_folder, rel_path)
            if os.path.exists(local_path) and os.path.getsize(local_path) == blob.size and not self.args.overwrite:
                print(f"Пропускаем {local_path} - файл уже существует с тем же размером")
                self.skipped_count += 1
                continue
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            print(f"Скачиваем gs://{bucket_name}/{blob.name} → {local_path}")
            blob.download_to_filename(local_path)
            self.uploaded_count += 1  # Можно переименовать счетчик в processed_count
            print(f"Скачан {local_path}")

    def download_from_huggingface(self):
        try:
            from huggingface_hub import HfApi, HfFolder, hf_hub_download
        except ImportError:
            print("Ошибка: Для работы с Hugging Face необходимо установить библиотеку huggingface_hub")
            print("Выполните: pip install huggingface_hub")
            sys.exit(1)
        
        if not self.args.hf_repo_id:
            print("Ошибка: Для Hugging Face необходимо указать ID репозитория (--hf_repo_id)")
            sys.exit(1)
        
        token = self.args.hf_token
        if not token:
            token = HfFolder.get_token()
            if not token:
                print("Ошибка: Токен Hugging Face не указан и не найден в кэше.")
                print("Используйте --hf_token или выполните 'huggingface-cli login'")
                sys.exit(1)
        
        api = HfApi()
        print(f"Получение списка файлов в репозитории {self.args.hf_repo_id}...")
        try:
            repo_files = api.list_repo_files(repo_id=self.args.hf_repo_id, token=token)
            files_info = {}
            for file_path in repo_files:
                try:
                    file_info = api.get_info_from_repo(
                        repo_id=self.args.hf_repo_id,
                        filename=file_path,
                        token=token
                    )
                    if hasattr(file_info, 'size'):
                        files_info[file_path] = file_info.size
                    else:
                        files_info[file_path] = None
                except Exception as e:
                    print(f"Не удалось получить информацию о файле {file_path}: {e}")
                    files_info[file_path] = None
            print(f"Найдено {len(repo_files)} файлов в репозитории")
        except Exception as e:
            print(f"Ошибка при получении списка файлов: {e}")
            repo_files = []
            files_info = {}
        
        import shutil
        for file_path in repo_files:
            local_path = os.path.join(self.args.local_folder, file_path)
            expected_size = files_info.get(file_path)
            if os.path.exists(local_path) and expected_size is not None and os.path.getsize(local_path) == expected_size and not self.args.overwrite:
                print(f"Пропускаем {local_path} - файл уже существует с тем же размером")
                self.skipped_count += 1
                continue
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            print(f"Скачиваем {self.args.hf_repo_id}/{file_path} → {local_path}")
            try:
                downloaded_path = hf_hub_download(
                    repo_id=self.args.hf_repo_id,
                    filename=file_path,
                    token=token,
                    repo_type="model"
                )
                shutil.copy2(downloaded_path, local_path)
                self.uploaded_count += 1
                print(f"Скачан {local_path}")
            except Exception as e:
                print(f"Ошибка при скачивании {file_path}: {e}")

    def download_from_s3(self):
        try:
            import boto3
        except ImportError:
            print("Ошибка: Для работы с AWS S3 необходимо установить библиотеку boto3")
            print("Выполните: pip install boto3")
            sys.exit(1)
        
        if not self.args.s3_bucket:
            print("Ошибка: Для AWS S3 необходимо указать имя бакета (--s3_bucket)")
            sys.exit(1)
        
        s3_kwargs = {'region_name': self.args.s3_region}
        if self.args.s3_access_key and self.args.s3_secret_key:
            s3_kwargs['aws_access_key_id'] = self.args.s3_access_key
            s3_kwargs['aws_secret_access_key'] = self.args.s3_secret_key
        
        s3 = boto3.client('s3', **s3_kwargs)
        
        print(f"Получение списка файлов в бакете S3 {self.args.s3_bucket} с префиксом {self.args.s3_prefix}...")
        s3_files = {}
        try:
            paginator = s3.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=self.args.s3_bucket, Prefix=self.args.s3_prefix)
            for page in pages:
                if 'Contents' in page:
                    for obj in page['Contents']:
                        s3_files[obj['Key']] = obj['Size']
            print(f"Найдено {len(s3_files)} файлов в бакете S3")
        except Exception as e:
            print(f"Ошибка при получении списка файлов из S3: {e}")
            s3_files = {}
        
        for key, size in s3_files.items():
            if not key.startswith(self.args.s3_prefix):
                continue
            rel_path = key[len(self.args.s3_prefix):]
            local_path = os.path.join(self.args.local_folder, rel_path)
            if os.path.exists(local_path) and os.path.getsize(local_path) == size and not self.args.overwrite:
                print(f"Пропускаем {local_path} - файл уже существует с тем же размером")
                self.skipped_count += 1
                continue
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            print(f"Скачиваем s3://{self.args.s3_bucket}/{key} → {local_path}")
            try:
                s3.download_file(self.args.s3_bucket, key, local_path)
                self.uploaded_count += 1
                print(f"Скачан {local_path}")
            except Exception as e:
                print(f"Ошибка при скачивании {key} из S3: {e}")

    def run(self):
        if self.args.action == 'upload':
            if self.args.storage == 'google':
                self.upload_to_google()
            elif self.args.storage == 'huggingface':
                self.upload_to_huggingface()
            elif self.args.storage == 's3':
                self.upload_to_s3()
            else:
                print(f"Неизвестный тип хранилища: {self.args.storage}")
                sys.exit(1)
        elif self.args.action == 'download':
            if self.args.storage == 'google':
                self.download_from_google()
            elif self.args.storage == 'huggingface':
                self.download_from_huggingface()
            elif self.args.storage == 's3':
                self.download_from_s3()
            else:
                print(f"Неизвестный тип хранилища: {self.args.storage}")
                sys.exit(1)
        else:
            print(f"Неизвестное действие: {self.args.action}")
            sys.exit(1)
        
        print(f"✅ Операция завершена! Обработано: {self.uploaded_count}, пропущено: {self.skipped_count}, скрытых директорий пропущено: {self.hidden_dirs_skipped}")

# python model_manager.py --action upload --storage google --gcs_bucket your_bucket_name --gcs_prefix models/ --local_folder workspace/models --gcs_credentials /workspace/models/gcs_credentials.json
# python model_manager.py --action download --storage google --gcs_bucket your_bucket_name --gcs_prefix models/ --local_folder workspace/models --gcs_credentials /workspace/models/gcs_credentials.json
# bucket echeg_model_storage
if __name__ == '__main__':
    uploader = ModelManager()
    uploader.run()