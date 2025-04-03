import os
import json
import requests
from dotenv import load_dotenv
import unittest

# Загружаем переменные окружения из .env файла
load_dotenv()

class TestRunpodAPI(unittest.TestCase):
    def setUp(self):
        """Настройка тестового окружения"""
        self.api_key = os.getenv('RUNPOD_API_KEY')
        self.endpoint_id = os.getenv('RUNPOD_ENDPOINT_ID')
        self.base_url = f"https://api.runpod.ai/v2/{self.endpoint_id}"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Загружаем workflow из JSON файла
        workflow_path = os.path.join(os.path.dirname(__file__), 'workflow.json')
        with open(workflow_path, 'r') as f:
            self.workflow = json.load(f)

    def test_generate_image(self):
        """Тест генерации изображения через RunPod API"""
        # Подготовка данных для запроса
        data = {
            "input": {
                "workflow": self.workflow
            }
        }

        # Отправка запроса
        response = requests.post(
            f"{self.base_url}/runsync",
            headers=self.headers,
            json=data
        )

        # Проверка ответа
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIn("output", response_data)
        self.assertIn("status", response_data["output"])
        self.assertEqual(response_data["output"]["status"], "success")

if __name__ == '__main__':
    unittest.main() 